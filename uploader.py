import requests
import json
import time
import os
import config
from logger import log_info, log_error

FAILED_UPLOADS_FILE = "failed_uploads.jsonl"

def upload_article(article_data, max_retries=3, retry_delay=5):
    """
    Upload an article dictionary to the Django backend API.
    The article_data should contain all article fields including:
    headline, category, summaries, mood, sources, thumbnails, audio paths, timestamps.
    """
    url = f"{config.API_BASE_URL}/articles/"
    headers = {"Content-Type": "application/json"}

    # Inject the secret source code for backend verification
    payload = {**article_data, "source_code": config.API_SECRET_CODE}

    for attempt in range(1, max_retries + 1):
        try:
            log_info(f"Uploading article: '{article_data.get('headline', 'No headline')[:50]}...' (Attempt {attempt})")
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            response.raise_for_status()
            log_info(f"Upload successful with status {response.status_code}")
            return True
        except requests.RequestException as e:
            log_error(f"Upload attempt {attempt} failed: {e}")
            if attempt < max_retries:
                log_info(f"Retrying upload after {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                log_error(f"All {max_retries} upload attempts failed for: {article_data.get('headline', '')[:50]}")
                return False

def save_failed_article(article_data):
    """
    Append failed article data as JSON line for retrying later.
    """
    try:
        with open(FAILED_UPLOADS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(article_data, ensure_ascii=False) + '\n')
        log_info(f"Saved failed article for retry: {article_data.get('headline', '')[:50]}")
    except Exception as e:
        log_error(f"Failed to save article for retry: {e}")

def load_failed_articles():
    """
    Load all failed article JSON lines from file.
    """
    if not os.path.exists(FAILED_UPLOADS_FILE):
        return []
    try:
        with open(FAILED_UPLOADS_FILE, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        log_error(f"Failed to load failed articles: {e}")
        return []

def clear_failed_articles():
    """
    Remove the failed uploads file to clear all saved failures.
    """
    try:
        if os.path.exists(FAILED_UPLOADS_FILE):
            os.remove(FAILED_UPLOADS_FILE)
            log_info("Cleared all failed uploads.")
    except Exception as e:
        log_error(f"Error clearing failed uploads: {e}")

def retry_failed_uploads():
    """
    Retry uploading all failed articles, save those still failing again.
    """
    failed_articles = load_failed_articles()
    if not failed_articles:
        log_info("No failed uploads to retry.")
        return

    log_info(f"Retrying {len(failed_articles)} failed upload(s)...")
    remaining = []

    for article in failed_articles:
        success = upload_article(article)
        if not success:
            remaining.append(article)

    if remaining:
        try:
            with open(FAILED_UPLOADS_FILE, 'w', encoding='utf-8') as f:
                for article in remaining:
                    f.write(json.dumps(article, ensure_ascii=False) + '\n')
            log_error(f"{len(remaining)} failed upload(s) remain after retry.")
        except Exception as e:
            log_error(f"Failed to re-save remaining failed uploads: {e}")
    else:
        clear_failed_articles()
        log_info("All failed uploads succeeded on retry.")
