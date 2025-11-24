from api_client import call_perplexity_api
from logger import log_info, log_success, log_error, log_warning
import json

def process_article_single_call(category, word_count):
    """
    OPTIMIZED: Single API call that does everything
    """
    
    prompt = build_prompt(category, word_count)
    response = call_perplexity_api(prompt)
    
    log_info(f"Processing {category} article ({word_count} words)", module="content_generator")
    
    response = call_perplexity_api(prompt)
    if not response:
        log_error(f"No response for {category}", module="content_generator")
        return None
    
    try:
        # Parse JSON response
        cleaned = response.strip()
        if cleaned.startswith('```'):
            cleaned = cleaned[7:]
        if cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        data = json.loads(cleaned)
        
        log_success(f"Article generated for {category} | Mood: {data.get('mood', 'neutral')}", module="content_generator")
        
        return data
        
    except json.JSONDecodeError as e:
        log_error(f"JSON parse failed for {category}: {e}", module="content_generator")
        log_warning(f"Raw response: {response[:100]}...", module="content_generator")
        return None


def build_prompt(category, word_count):
    if category in ['concours_launch', 'exam_results']:
        return f"""
        You are the best news curator journalist specialized in Cameroon’s education and competition sector.
        1. Search Cameroonian news sources for official announcements from national right up to divisional levels or results of national, regional or other exams even international exams and concours where cameroonians participated published in the last 10 days.
        2. Write a {word_count}-word summary in FRENCH using professional, punchy Cameroonian journalism style
        3. Write a {word_count}-word summary in ENGLISH using professional, punchy Cameroonian journalism style
        4. Identify the emotional mood (choose one: happy, angry, sad, exciting, shocking, inspiring, concerning, neutral)
        Return ALL sources linked to this story (with URLs and source names).
        Provide mood classification (happy, angry, sad, exciting, shocking, inspiring, concerning, neutral).
        
        Return your response in this EXACT JSON format:
        {{
          "headline": "Brief headline",
          "source_urls": [
            "https://camer.be/article1",
            "https://examresults.cm/article2"
          ],
          "source_names": [
            "camer.be",
            "examresults.cm"
          ],
          "french_summary": "French summary...",
          "english_summary": "English summary...",
          "mood": "mood word"
        }}
        
        Return ONLY valid JSON, nothing else.
        """
    elif category == 'latest_jobs':
        return f"""
        You are the best news curator journalist specialized in Cameroon’s job market and employment sector.
        1. Search Cameroonian news sources for official job announcements and recruitment ads from national down to divisional and local levels published in the last 10 days.
        2. Write a {word_count}-word summary in FRENCH using professional, punchy Cameroonian journalism style.
        3. Write a {word_count}-word summary in ENGLISH using professional, punchy Cameroonian journalism style.
        4. Identify the emotional mood (choose one: happy, angry, sad, exciting, shocking, inspiring, concerning, neutral).
        Return ALL sources linked to this story (with URLs and source names).
        Provide mood classification (happy, angry, sad, exciting, shocking, inspiring, concerning, neutral).
        
        Return your response in this EXACT JSON format:
        {{
          "headline": "Brief headline",
          "source_urls": [
            "https://jobportal.cm/article1",
            "https://division.cameroonjobs.org/article2"
          ],
          "source_names": [
            "jobportal.cm",
            "cameroonjobs.org"
          ],
          "french_summary": "French summary...",
          "english_summary": "English summary...",
          "mood": "mood word"
        }}
        
        Return ONLY valid JSON, nothing else.
        """
    
    else:
        # Your original generalized prompt
        return f"""
        You are the best Cameroonian news journalist curator. Complete this task in ONE response:

        1. Search for the latest {category} news from Cameroon (LOCAL news only, not general African news)
        2. Write a {word_count}-word summary in FRENCH using raw, punchy Cameroonian journalism style
        3. Write a {word_count}-word summary in ENGLISH using raw, punchy Cameroonian journalism style
        4. Identify the emotional mood (choose one: happy, angry, sad, exciting, shocking, inspiring, concerning, neutral)

        Style requirements for summaries:
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
