import os
import logging
from gtts import gTTS
import config


def log_error(message):
    """Log errors to file"""
    logging.error(message)
    print(f"❌ MEDIA ERROR: {message}")


def generate_audio(text, language, filename):
    """
    Generate TTS audio file
    Returns: filepath on success, None on failure
    """
    try:
        lang_code = 'fr' if language == 'french' else 'en'
        audio_dir = config.AUDIO_DIR_FRENCH if language == 'french' else config.AUDIO_DIR_ENGLISH
        
        filepath = os.path.join(audio_dir, filename)
        
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(filepath)
        
        print(f"🔊 Generated {language} audio: {filename}")
        return filepath
    
    except Exception as e:
        log_error(f"TTS generation failed for {language}: {str(e)}")
        return None


def extract_thumbnail(source_url, filename):
    """
    Extract or generate thumbnail
    Returns: filepath on success, None on failure
    For MVP, this is a placeholder - implement later with BeautifulSoup or AI image generation
    """
    print(f"📷 Thumbnail placeholder: {filename}")
    # TODO: Implement actual thumbnail extraction/generation
    return None
