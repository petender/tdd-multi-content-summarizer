import azure.functions as func
import logging
import json
import os
from shared.video_processor import extract_video_id, fetch_transcript
from shared.openai_client import summarize_transcript, summarize_content
from shared.cosmos_client import save_video_summary, get_video_summary
from shared.web_scraper import fetch_article_content
from shared.pdf_processor import extract_pdf_text
from shared.text_processor import process_text_input
from datetime import datetime
import base64

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="summarize", methods=["POST"])
async def summarize_video(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function to summarize a video from URL.
    Expects JSON body: { "videoUrl": "https://youtube.com/watch?v=...", "userId": "user123", "language": "English" }
    """
    logging.info('=== Summarize video function triggered ===')

    try:
        req_body = req.get_json()
        logging.info(f'Request body: {req_body}')
        video_url = req_body.get('videoUrl')
        user_id = req_body.get('userId', 'anonymous')
        language = req_body.get('language', 'English')
        logging.info(f'Processing video URL: {video_url} for user: {user_id} in {language}')

        if not video_url:
            return func.HttpResponse(
                json.dumps({"error": "videoUrl is required"}),
                mimetype="application/json",
                status_code=400
            )

        # Extract video ID
        video_id = extract_video_id(video_url)
        logging.info(f'Extracted video ID: {video_id} from URL: {video_url}')
        if not video_id:
            return func.HttpResponse(
                json.dumps({"error": "Invalid video URL"}),
                mimetype="application/json",
                status_code=400
            )

        # Check if already processed (skip if COSMOS_ENDPOINT not configured)
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        if cosmos_endpoint:
            try:
                existing_summary = await get_video_summary(video_id, user_id)
                if existing_summary:
                    return func.HttpResponse(
                        json.dumps(existing_summary),
                        mimetype="application/json",
                        status_code=200
                    )
            except Exception as e:
                logging.warning(f'Could not check existing summary: {str(e)}')

        # Fetch transcript
        logging.info(f'Fetching transcript for video ID: {video_id}')
        transcript_data = fetch_transcript(video_id)
        logging.info(f'Transcript fetch result: {transcript_data is not None}')
        if not transcript_data:
            error_msg = (
                "Could not fetch transcript for this video. "
                "This may be due to YouTube blocking requests from cloud providers. "
                "The video must have captions/subtitles available. "
                "Try running the application locally or use a video that has been tested to work."
            )
            return func.HttpResponse(
                json.dumps({"error": error_msg}),
                mimetype="application/json",
                status_code=404
            )

        transcript_text = transcript_data['text']
        
        # Summarize with OpenAI
        summary = await summarize_transcript(transcript_text, video_id, language)
        
        # Save to Cosmos DB (skip if not configured)
        video_data = {
            "id": video_id,
            "userId": user_id,
            "videoUrl": video_url,
            "videoId": video_id,
            "transcript": transcript_text,
            "summary": summary,
            "timestamps": transcript_data.get('timestamps', []),
            "createdAt": datetime.utcnow().isoformat(),
            "duration": transcript_data.get('duration', 0)
        }
        
        if cosmos_endpoint:
            try:
                await save_video_summary(video_data)
                logging.info(f'Saved summary to Cosmos DB for video {video_id}')
            except Exception as e:
                logging.warning(f'Could not save to Cosmos DB: {str(e)}')

        return func.HttpResponse(
            json.dumps(video_data),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error processing video: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="history/{userId}", methods=["GET"])
async def get_history(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get user's video summary history.
    """
    logging.info('Get history function triggered.')

    try:
        user_id = req.route_params.get('userId')
        
        if not user_id:
            return func.HttpResponse(
                json.dumps({"error": "userId is required"}),
                mimetype="application/json",
                status_code=400
            )

        from shared.cosmos_client import get_user_history
        history = await get_user_history(user_id)

        return func.HttpResponse(
            json.dumps({"history": history}),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error fetching history: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="test-transcript", methods=["POST"])
async def test_transcript(req: func.HttpRequest) -> func.HttpResponse:
    """
    Diagnostic endpoint to test transcript fetching with detailed logging.
    """
    logging.info('=== Test transcript endpoint triggered ===')

    try:
        req_body = req.get_json()
        video_url = req_body.get('videoUrl')
        logging.info(f'Testing video URL: {video_url}')

        if not video_url:
            return func.HttpResponse(
                json.dumps({"error": "videoUrl is required"}),
                mimetype="application/json",
                status_code=400
            )

        # Extract video ID
        video_id = extract_video_id(video_url)
        logging.info(f'Extracted video ID: {video_id}')
        
        if not video_id:
            return func.HttpResponse(
                json.dumps({"error": "Invalid video URL", "videoId": None}),
                mimetype="application/json",
                status_code=400
            )

        # Try to fetch transcript with detailed logging
        logging.info(f'Starting transcript fetch for: {video_id}')
        transcript_data = fetch_transcript(video_id)
        logging.info(f'Transcript fetch completed. Success: {transcript_data is not None}')
        
        if transcript_data:
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "videoId": video_id,
                    "textLength": len(transcript_data['text']),
                    "segmentCount": len(transcript_data['timestamps']),
                    "duration": transcript_data.get('duration'),
                    "preview": transcript_data['text'][:200]
                }),
                mimetype="application/json",
                status_code=200
            )
        else:
            logging.error(f'Failed to fetch transcript for {video_id}')
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "videoId": video_id,
                    "error": "Could not fetch transcript - check logs for details"
                }),
                mimetype="application/json",
                status_code=404
            )

    except Exception as e:
        logging.error(f"Error in test endpoint: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e), "type": type(e).__name__}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="summarize-article", methods=["POST"])
async def summarize_article(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function to summarize a web article from URL.
    Expects JSON body: { "articleUrl": "https://...", "userId": "user123", "language": "English" }
    """
    logging.info('=== Summarize article function triggered ===')

    try:
        req_body = req.get_json()
        article_url = req_body.get('articleUrl')
        user_id = req_body.get('userId', 'anonymous')
        language = req_body.get('language', 'English')

        if not article_url:
            return func.HttpResponse(
                json.dumps({"error": "articleUrl is required"}),
                mimetype="application/json",
                status_code=400
            )

        # Fetch article content
        logging.info(f'Fetching article from: {article_url}')
        article_data = fetch_article_content(article_url)
        
        if not article_data:
            return func.HttpResponse(
                json.dumps({"error": "Could not fetch article content. Please check the URL."}),
                mimetype="application/json",
                status_code=404
            )

        # Summarize with OpenAI
        logging.info(f'Summarizing article in {language}')
        summary = await summarize_content(
            article_data['text'],
            article_url,
            language,
            "article"
        )
        
        response_data = {
            "title": article_data.get('title', 'Untitled'),
            "author": article_data.get('author', 'Unknown'),
            "url": article_url,
            "summary": summary,
            "language": language,
            "createdAt": datetime.utcnow().isoformat()
        }

        return func.HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error summarizing article: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="summarize-text", methods=["POST"])
async def summarize_text(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function to summarize direct text input.
    Expects JSON body: { "text": "...", "userId": "user123", "language": "English" }
    """
    logging.info('=== Summarize text function triggered ===')

    try:
        req_body = req.get_json()
        text_content = req_body.get('text')
        user_id = req_body.get('userId', 'anonymous')
        language = req_body.get('language', 'English')

        if not text_content:
            return func.HttpResponse(
                json.dumps({"error": "text is required"}),
                mimetype="application/json",
                status_code=400
            )

        # Process text input
        text_data = process_text_input(text_content)
        
        if not text_data:
            return func.HttpResponse(
                json.dumps({"error": "Text is too short. Please provide at least 50 characters."}),
                mimetype="application/json",
                status_code=400
            )

        # Summarize with OpenAI
        logging.info(f'Summarizing text input in {language}')
        summary = await summarize_content(
            text_data['text'],
            f"text_{user_id}",
            language,
            "text"
        )
        
        response_data = {
            "word_count": text_data['word_count'],
            "char_count": text_data['char_count'],
            "summary": summary,
            "language": language,
            "createdAt": datetime.utcnow().isoformat()
        }

        return func.HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error summarizing text: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="summarize-pdf", methods=["POST"])
async def summarize_pdf(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function to summarize a PDF file.
    Expects JSON body: { "pdfBase64": "...", "filename": "doc.pdf", "userId": "user123", "language": "English" }
    """
    logging.info('=== Summarize PDF function triggered ===')

    try:
        req_body = req.get_json()
        pdf_base64 = req_body.get('pdfBase64')
        filename = req_body.get('filename', 'document.pdf')
        user_id = req_body.get('userId', 'anonymous')
        language = req_body.get('language', 'English')

        if not pdf_base64:
            return func.HttpResponse(
                json.dumps({"error": "pdfBase64 is required"}),
                mimetype="application/json",
                status_code=400
            )

        # Decode PDF from base64
        try:
            pdf_bytes = base64.b64decode(pdf_base64)
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": f"Invalid PDF encoding: {str(e)}"}),
                mimetype="application/json",
                status_code=400
            )

        # Extract text from PDF
        logging.info(f'Extracting text from PDF: {filename}')
        pdf_data = extract_pdf_text(pdf_bytes, filename)
        
        if not pdf_data:
            return func.HttpResponse(
                json.dumps({"error": "Could not extract text from PDF. Please ensure it contains readable text."}),
                mimetype="application/json",
                status_code=404
            )

        # Summarize with OpenAI
        logging.info(f'Summarizing PDF in {language}')
        summary = await summarize_content(
            pdf_data['text'],
            filename,
            language,
            "pdf"
        )
        
        response_data = {
            "filename": pdf_data['filename'],
            "pages": pdf_data['pages'],
            "summary": summary,
            "language": language,
            "createdAt": datetime.utcnow().isoformat()
        }

        return func.HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error summarizing PDF: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
