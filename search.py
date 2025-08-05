import os
import requests
from logger import setup_logger
from dotenv import load_dotenv

logger = setup_logger('nanomaterial_search')

def search_papers(category, num_results):
    """Search for papers using Serper Google Search API based on category."""
    try:
        load_dotenv()
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            logger.error("SERPER_API_KEY not found in .env")
            return []

        query = f"{category} synthesis parameters filetype:pdf"
        url = "https://google.serper.dev/search"
        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        payload = {"q": query, "num": min(num_results, 10)}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json().get("organic", [])
        formatted_results = [
            {"title": item.get("title", "Untitled"), "url": item.get("link", "")}
            for item in results[:min(num_results, 10)]
        ]
        logger.info(f"Fetched {len(formatted_results)} papers for category: {category}")
        return formatted_results
    except Exception as e:
        logger.error(f"Error searching papers: {str(e)}")
        return []