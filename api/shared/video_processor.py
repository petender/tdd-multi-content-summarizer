"""
Video processing utilities for extracting video IDs and fetching transcripts.
"""
import re
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, RequestBlocked

def extract_video_id(url: str) -> str:
    """
    Extract video ID from various YouTube URL formats.
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def fetch_transcript(video_id: str) -> dict:
    """
    Fetch transcript for a YouTube video.
    Returns dict with 'text' (full transcript) and 'timestamps' (list of segments).
    Note: May fail in cloud environments due to YouTube blocking cloud provider IPs.
    """
    logging.info(f'=== Starting transcript fetch for video ID: {video_id} ===')
    try:
        # Fetch transcript (tries to get English first, then any available)
        logging.info('Calling YouTubeTranscriptApi.list...')
        # Create instance and call list
        yt_api = YouTubeTranscriptApi()
        transcript_list = yt_api.list(video_id)
        logging.info(f'Successfully retrieved transcript list for video {video_id}')
        
        # Try multiple approaches to get a transcript
        transcript = None
        last_error = None
        
        # 1. Try manually created English transcript
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
            logging.info(f"Found manually created English transcript for {video_id}")
        except Exception as e:
            logging.debug(f"No manually created transcript: {str(e)}")
            last_error = e
        
        # 2. Try auto-generated English transcript
        if not transcript:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
                logging.info(f"Found auto-generated English transcript for {video_id}")
            except Exception as e:
                logging.debug(f"No auto-generated transcript: {str(e)}")
                last_error = e
        
        # 3. Try any English transcript
        if not transcript:
            try:
                transcript = transcript_list.find_transcript(['en'])
                logging.info(f"Found English transcript for {video_id}")
            except Exception as e:
                logging.debug(f"No English transcript: {str(e)}")
                last_error = e
        
        # 4. Try any available transcript and translate to English
        if not transcript:
            try:
                # Get any available transcript
                available_transcripts = list(transcript_list)
                logging.info(f"Available transcripts: {[str(t) for t in available_transcripts]}")
                if available_transcripts:
                    transcript = available_transcripts[0].translate('en')
                    logging.info(f"Translated transcript to English for {video_id}")
            except Exception as e:
                logging.debug(f"Could not translate transcript: {str(e)}")
                last_error = e
        
        if not transcript:
            logging.error(f"No transcript available for video {video_id}. Last error: {str(last_error)}")
            return None
        
        logging.info(f"Fetching transcript data for {video_id}...")
        transcript_data = transcript.fetch()
        logging.info(f"Successfully fetched {len(transcript_data)} transcript segments")
        
        # Build full text from transcript segments
        # Note: transcript_data items are dataclass objects, use attributes not dict access
        full_text = ' '.join([entry.text for entry in transcript_data])
        
        # Extract timestamps for navigation
        timestamps = [
            {
                'time': entry.start,
                'text': entry.text
            }
            for entry in transcript_data
        ]
        
        duration = transcript_data[-1].start + transcript_data[-1].duration if transcript_data else 0
        
        return {
            'text': full_text,
            'timestamps': timestamps,
            'duration': duration
        }
    
    except RequestBlocked as e:
        logging.error(f"[TRANSCRIPT ERROR] YouTube blocked the request for video {video_id}")
        logging.error("This typically happens when running in cloud environments (Azure, AWS, GCP)")
        logging.error("YouTube blocks requests from cloud provider IP addresses")
        return None
    except TranscriptsDisabled:
        logging.error(f"[TRANSCRIPT ERROR] Transcripts are disabled for video {video_id}")
        return None
    except NoTranscriptFound:
        logging.error(f"[TRANSCRIPT ERROR] No transcript found for video {video_id}")
        return None
    except AttributeError as e:
        logging.error(f"[TRANSCRIPT ERROR] AttributeError for video {video_id}: {str(e)}", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"[TRANSCRIPT ERROR] Unexpected error fetching transcript for video {video_id}: {str(e)}", exc_info=True)
        logging.error(f"[TRANSCRIPT ERROR] Exception type: {type(e).__name__}")
        import traceback
        logging.error(f"[TRANSCRIPT ERROR] Full traceback: {traceback.format_exc()}")
        return None
