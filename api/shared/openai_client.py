"""
Azure OpenAI client for summarizing content and translating to multiple languages.
"""
import os
import logging
from openai import AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Configuration
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

# Lazy initialization
_client = None
_token_provider = None

def get_client():
    """Get or create Azure OpenAI client."""
    global _client, _token_provider
    if _client is None:
        if not endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set")
        _token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )
        _client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=_token_provider,
            api_version="2024-02-01"
        )
    return _client

async def summarize_content(content: str, content_id: str, target_language: str = "English", content_type: str = "content") -> dict:
    """
    Summarize content using Azure OpenAI GPT-4 and translate to target language.
    
    Args:
        content: The text content to summarize
        content_id: Identifier for logging
        target_language: Target language for summary (English, French, German, Spanish, Japanese, Hindi, etc.)
        content_type: Type of content (video, article, text, pdf) for context
        
    Returns:
        Structured summary with key points, topics, and action items in the target language
    """
    try:
        client = get_client()
        # Truncate if too long (stay within token limits)
        max_chars = 12000
        if len(content) > max_chars:
            content = content[:max_chars] + "..."
            logging.warning(f"Content truncated for {content_id}")

        # Build prompt based on language
        language_instruction = ""
        if target_language.lower() != "english":
            language_instruction = f"\n\nIMPORTANT: Provide the ENTIRE response in {target_language}. All sections must be in {target_language}."

        prompt = f"""Analyze the following {content_type} content and provide a structured summary:

Content:
{content}

Please provide:
1. Executive Summary (2-3 sentences)
2. Key Topics (bullet points)
3. Main Takeaways (3-5 points)
4. Action Items (if any){language_instruction}

Format the response as JSON with keys: executive_summary, key_topics (array), main_takeaways (array), action_items (array)"""

        system_message = f"You are an expert at analyzing and summarizing content. Provide clear, actionable summaries."
        if target_language.lower() != "english":
            system_message += f" Respond ONLY in {target_language}."

        response = await client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        summary_text = response.choices[0].message.content
        
        # Try to parse as JSON, fallback to text if it fails
        try:
            import json
            summary = json.loads(summary_text)
        except:
            summary = {
                "executive_summary": summary_text,
                "key_topics": [],
                "main_takeaways": [],
                "action_items": []
            }

        # Add language metadata
        summary['language'] = target_language

        return summary

    except Exception as e:
        logging.error(f"Error summarizing content: {str(e)}")
        raise Exception(f"OpenAI summarization failed: {str(e)}")


# Backward compatibility - keep old function name
async def summarize_transcript(transcript: str, video_id: str, target_language: str = "English") -> dict:
    """Legacy function name for backward compatibility."""
    return await summarize_content(transcript, video_id, target_language, "video")

