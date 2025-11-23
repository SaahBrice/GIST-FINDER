from api_client import call_perplexity_api
import json


def process_article_single_call(category, word_count):
    """
    OPTIMIZED: Single API call that does everything
    - Discovers news
    - Generates French summary
    - Generates English summary  
    - Detects mood
    Returns: dict with all data or None on failure
    """
    
    prompt = f"""
    You are a Cameroonian news curator. Complete this task in ONE response:

    1. Search for the latest {category} news from Cameroon (LOCAL news only, not general African news)
    2. Write a {word_count}-word summary in FRENCH using raw, punchy Cameroonian journalism style
    3. Write a {word_count}-word summary in ENGLISH using raw, punchy Cameroonian journalism style
    4. Identify the emotional mood (choose one: happy, angry, sad, exciting, shocking, inspiring, concerning, neutral)

    Style requirements for summaries:
    - Short, direct sentences that hit hard
    - Emotional, opinionated language
    - Colloquial expressions and local slang
    - Rhetorical questions
    - Write like texting a friend breaking news

    Return your response in this EXACT JSON format:
    {{
        "headline": "Brief headline",
        "source_url": "URL of original article",
        "french_summary": "Full French summary here",
        "english_summary": "Full English summary here",
        "mood": "mood word"
    }}

    Return ONLY valid JSON, nothing else.
    """
    
    print(f"🔍 Processing {category} (single optimized call)...")
    
    response = call_perplexity_api(prompt)
    if not response:
        return None
    
    try:
        # Parse JSON response
        # Sometimes the API adds markdown code blocks, so clean it
        cleaned = response.strip()
        if cleaned.startswith('```'):
            cleaned = cleaned[7:]
        if cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        data = json.loads(cleaned)
        
        print(f"✅ Got all data in one call!")
        print(f"   Headline: {data.get('headline', 'N/A')[:50]}...")
        print(f"   Mood: {data.get('mood', 'neutral')}")
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        print(f"Response was: {response[:200]}...")
        return None


# Keep these for backward compatibility if needed
def discover_cameroon_news(category):
    """Legacy function - kept for compatibility"""
    return process_article_single_call(category, 200)


def generate_cameroon_style_summary(raw_news, word_count, language):
    """Legacy function - kept for compatibility"""
    # This is now handled by process_article_single_call
    pass


def detect_mood(article_text):
    """Legacy function - kept for compatibility"""
    # This is now handled by process_article_single_call
    pass
