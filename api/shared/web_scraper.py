"""
Web article scraping utilities for extracting content from URLs.
"""
import logging
import requests
from bs4 import BeautifulSoup

def fetch_article_content(url: str) -> dict:
    """
    Fetch and extract content from a web article URL using BeautifulSoup.
    Returns dict with 'text' (article content), 'title', and 'author'.
    """
    logging.info(f'=== Starting article fetch for URL: {url} ===')
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get title
        title = soup.find('title')
        title_text = title.get_text() if title else 'Untitled'
        
        # Try to find main content - use multiple strategies
        main_content = None
        
        # Strategy 1: Look for semantic HTML5 tags
        for tag in ['article', 'main']:
            main_content = soup.find(tag)
            if main_content:
                break
        
        # Strategy 2: Look for common content class names
        if not main_content:
            for selector in [
                {'class': lambda x: x and 'content' in x.lower()},
                {'class': lambda x: x and 'post' in x.lower()},
                {'class': lambda x: x and 'article' in x.lower()},
                {'id': lambda x: x and 'content' in x.lower()},
                {'id': lambda x: x and 'main' in x.lower()}
            ]:
                main_content = soup.find('div', selector)
                if main_content:
                    break
        
        # Strategy 3: Find the div with most paragraph tags
        if not main_content:
            divs = soup.find_all('div')
            max_p_count = 0
            for div in divs:
                p_count = len(div.find_all('p'))
                if p_count > max_p_count:
                    max_p_count = p_count
                    main_content = div
        
        # Fallback: use body
        if not main_content:
            main_content = soup.find('body')
        
        # Extract text
        text = main_content.get_text(separator='\n', strip=True) if main_content else ''
        
        # Clean up text - remove extra whitespace and empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        # Remove very short lines (likely navigation/UI elements)
        lines = [line for line in lines if len(line) > 20]
        text = '\n\n'.join(lines)
        
        if text and len(text) > 100:
            logging.info(f"Successfully fetched article using BeautifulSoup: {title_text}")
            return {
                'text': text,
                'title': title_text,
                'author': 'Unknown',
                'url': url,
                'source': 'beautifulsoup'
            }
        else:
            logging.error(f"Extracted text too short: {len(text)} characters")
            return None
            
    except requests.RequestException as e:
        logging.error(f"Request error fetching article: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error fetching article content: {str(e)}", exc_info=True)
        return None
