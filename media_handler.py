import os
from gtts import gTTS
import config
from logger import log_error, log_success, log_info, log_warning

import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse



THUMBS_PER_ARTICLE = 5  # Max number of thumbnails per article




def generate_audio(text, language, filename):
    """
    Generate TTS audio file
    Returns: filepath on success, None on failure
    """
    try:
        log_info(f"Generating {language} audio...", module="media_handler")
        
        lang_code = 'fr' if language == 'french' else 'en'
        audio_dir = config.AUDIO_DIR_FRENCH if language == 'french' else config.AUDIO_DIR_ENGLISH
        
        filepath = os.path.join(audio_dir, filename)
        
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(filepath)
        
        log_success(f"Audio generated: {filename} ({language})", module="media_handler")
        return filepath
    
    except Exception as e:
        log_error(f"TTS generation failed for {language}: {str(e)}", module="media_handler")
        return None


def extract_thumbnail(source_url, filename):
    """
    Extract or generate thumbnail
    Returns: filepath on success, None on failure
    """
    log_info(f"Thumbnail placeholder: {filename}", module="media_handler")
    # TODO: Implement actual thumbnail extraction/generation
    return None


def is_logo_url(url):
    # Simple heuristic: filename/url contains 'logo' or 'icon'
    lower = url.lower()
    return 'logo' in lower or 'icon' in lower

def save_image_from_url(image_url, save_dir, filename_base, index):
    try:
        resp = requests.get(image_url, timeout=10)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        # Skip too small images (often logos or icons)
        if img.width < 100 or img.height < 100:
            return None
        
        ext = img.format.lower() if img.format else 'jpg'
        filename = f"{filename_base}_{index}.{ext}"
        filepath = os.path.join(save_dir, filename)
        img.save(filepath)
        return filepath
    except Exception as e:
        log_warning(f"Failed to save image {image_url}: {e}", module="media_handler")
        return None

def extract_thumbnails(source_url, category, filename_base):
    thumbnails = []
    save_dir = config.THUMBNAIL_DIR
    os.makedirs(save_dir, exist_ok=True)
    
    try:
        log_info(f"Extracting thumbnails from {source_url}", module="media_handler")
        resp = requests.get(source_url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Get all image URLs from <img> tags
        img_urls = []
        for img in soup.find_all('img', src=True):
            img_url = urljoin(source_url, img['src'])
            if not is_logo_url(img_url):
                img_urls.append(img_url)
        
        # Also check og:image meta tag
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content') and not is_logo_url(og_image['content']):
            img_urls.insert(0, urljoin(source_url, og_image['content']))
        
        # Remove duplicates preserving order
        seen = set()
        img_urls = [x for x in img_urls if not (x in seen or seen.add(x))]
        
        # Save up to THUMBS_PER_ARTICLE thumbnails
        for i, img_url in enumerate(img_urls[:THUMBS_PER_ARTICLE]):
            saved_path = save_image_from_url(img_url, save_dir, filename_base, i+1)
            if saved_path:
                thumbnails.append(saved_path)
        
        if thumbnails:
            log_info(f"Extracted {len(thumbnails)} thumbnails", module="media_handler")
            return thumbnails
        
    except Exception as e:
        log_warning(f"Failed to extract thumbnails: {e}, falling back to stock image", module="media_handler")
    
    # FALLBACK: Use stock image by category
    stock_image_path = os.path.join(config.THUMBNAIL_DIR, 'stock_images', f"{category}.jpg")
    if os.path.exists(stock_image_path):
        log_info(f"Using stock image fallback: {stock_image_path}", module="media_handler")
        return [stock_image_path]
    else:
        log_warning(f"No stock image found for category '{category}'", module="media_handler")
        return []

