import logging
from datetime import datetime
import config
from content_generator import process_article_single_call
from media_handler import generate_audio, extract_thumbnail


def log_error(message):
    """Log errors to file"""
    logging.error(message)
    print(f"❌ PROCESSOR ERROR: {message}")


def process_article(category):
    """
    OPTIMIZED: Main article processing pipeline
    Now uses single API call instead of 4!
    """
    try:
        print(f"\n{'='*60}")
        print(f"Processing {category.upper()} article...")
        print(f"{'='*60}\n")
        
        # Get random word count
        word_count = config.get_random_word_count()
        print(f"📏 Target length: {word_count} words\n")
        
        # SINGLE API CALL - gets everything at once!
        article_data = process_article_single_call(category, word_count)
        
        if not article_data:
            log_error(f"Failed to process {category}")
            return False
        
        # Extract data from response
        french_summary = article_data.get('french_summary')
        english_summary = article_data.get('english_summary')
        mood = article_data.get('mood', 'neutral')
        headline = article_data.get('headline', 'No headline')
        
        if not french_summary or not english_summary:
            log_error(f"Missing summaries for {category}")
            return False
        
        print(f"😊 Mood: {mood}\n")
        
        # Generate audio files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"{category}_{timestamp}.mp3"
        
        french_audio = generate_audio(french_summary, "french", audio_filename)
        if not french_audio:
            log_error(f"Failed to generate French audio for {category}")
            return False
        
        english_audio = generate_audio(english_summary, "english", audio_filename)
        if not english_audio:
            log_error(f"Failed to generate English audio for {category}")
            return False
        
        # Extract thumbnail
        thumbnail = extract_thumbnail(article_data.get('source_url', ''), f"{category}_{timestamp}.jpg")
        
        # Display results
        print(f"\n{'='*60}")
        print(f"✅ ARTICLE PROCESSED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"Headline: {headline}")
        print(f"Category: {category}")
        print(f"Mood: {mood}")
        print(f"Word Count: {word_count}")
        print(f"\n📝 FRENCH SUMMARY:\n{french_summary[:200]}...")
        print(f"\n📝 ENGLISH SUMMARY:\n{english_summary[:200]}...")
        print(f"\n🔊 French Audio: {french_audio}")
        print(f"🔊 English Audio: {english_audio}")
        print(f"📷 Thumbnail: {thumbnail}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        log_error(f"Article processing failed for {category}: {str(e)}")
        return False


def fetch_news_batch():
    """Fetch news for all categories"""
    print(f"\n🚀 Starting news batch at {datetime.now()}")
    print(f"{'='*60}\n")
    
    success_count = 0
    fail_count = 0
    
    for category in config.CATEGORIES:
        if process_article(category):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 BATCH SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"⚡ API Calls Saved: {success_count * 3} (75% reduction!)")
    print(f"✅ Batch completed at {datetime.now()}\n")
