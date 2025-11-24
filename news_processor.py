from datetime import datetime
import config
from content_generator import process_article_single_call
from media_handler import extract_thumbnails, generate_audio
from logger import log_info, log_success, log_error, log_warning, create_progress_bar, console
from deduplication import is_duplicate, save_article, max_hours, allowed_similarity
from uploader import upload_article, save_failed_article


def process_article(category):
    """Main article processing pipeline"""
    
    try:
        console.rule(f"[bold blue]{category.upper()}[/bold blue]")
        
        word_count = config.get_random_word_count()
        log_info(f"Target: {word_count} words", module="news_processor")
        
        # Single API call
        article_data = process_article_single_call(category, word_count)
        
        if not article_data:
            log_error(f"Failed to get article data for {category}", module="news_processor")
            return False
        
        headline = article_data.get('headline', 'No headline')
        source = article_data.get('source_url', '')

        # Use x hours (x/24 days) for deduplication time window
        if is_duplicate(headline, category, allowed_similarity, max_hours):
            log_info(f"SKIPPED as duplicate: {headline[:60]}", module='news_processor')
            return False  # Don't process further

        # Save to deduplication DB
        save_article(headline, category, source)
        
        french_summary = article_data.get('french_summary')
        english_summary = article_data.get('english_summary')
        mood = article_data.get('mood', 'neutral')
        headline = article_data.get('headline', 'No headline')
        
        # Validate presence of summaries
        if not french_summary or not english_summary:
            log_error(f"Missing summaries for {category}", module="news_processor")
            return False
        
        # Generate audio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"{category}_{timestamp}.mp3"
        
        french_audio = generate_audio(french_summary, "french", audio_filename)
        english_audio = generate_audio(english_summary, "english", audio_filename)
        
        if not french_audio or not english_audio:
            log_error(f"Audio generation failed for {category}", module="news_processor")
            return False
        
        # Extract thumbnails
        filename_base = f"{category}_{timestamp}"
        source_url = article_data.get('source_urls', [None])[0]  # Primary source or first available

        thumbnails = []
        if source_url:
            thumbnails = extract_thumbnails(source_url, category, filename_base)
        if not thumbnails:
            log_warning(f"No thumbnails found for {category} article", module="news_processor")
        
        # Success summary logs
        log_success(f"✨ {category.upper()} completed | {headline[:40]}...", module="news_processor")
        console.print(f"   📝 FR: {french_summary[:80]}...")
        console.print(f"   📝 EN: {english_summary[:80]}...")
        console.print(f"   🎭 Mood: {mood} | 🔊 Audio: ✓ | 📷 Thumb: {'✓' if thumbnails else '✗'}\n")
        
        # Prepare article data for upload    
        article_data_to_upload = {
            "headline": headline,
            "category": category,
            "french_summary": french_summary,
            "english_summary": english_summary,
            "mood": mood,
            "source_urls": article_data.get("source_urls", []),
            "source_names": article_data.get("source_names", []),
            "thumbnails": thumbnails,
            "french_audio": french_audio,
            "english_audio": english_audio,
            "timestamp": timestamp,
        }

        # Upload with retry support
        upload_success = upload_article(article_data_to_upload)
        if upload_success:
            log_info(f"Article uploaded successfully: {headline[:50]}...", module="news_processor")
        else:
            log_error(f"Article upload failed: {headline[:50]}... Saving for retry.", module="news_processor")
            save_failed_article(article_data_to_upload)

        return True
        
    except Exception as e:
        log_error(f"Processing failed for {category}: {str(e)}", module="news_processor")
        return False


def fetch_news_batch():
    """Fetch news for all categories with progress bar"""
    log_info(f"Starting batch at {datetime.now()}", module="news_processor")
    console.rule("[bold green]🚀 NEWS BATCH STARTED[/bold green]")
    
    success_count = 0
    fail_count = 0
    
    progress = create_progress_bar(len(config.CATEGORIES), "Processing articles")
    
    with progress:
        task = progress.add_task("[cyan]Processing...", total=len(config.CATEGORIES))
        
        for category in config.CATEGORIES:
            if process_article(category):
                success_count += 1
            else:
                fail_count += 1
            progress.update(task, advance=1)
    
    console.rule("[bold green]📊 BATCH COMPLETE[/bold green]")
    console.print(f"✅ Successful: [green]{success_count}[/green]")
    console.print(f"❌ Failed: [red]{fail_count}[/red]")
    console.print(f"⚡ API calls saved: [yellow]{success_count * 3}[/yellow] (75% reduction)")
    log_success(f"Batch complete: {success_count} success, {fail_count} failed", module="news_processor")
