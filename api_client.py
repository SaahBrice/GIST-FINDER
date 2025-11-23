import requests
import logging
import config

def log_error(message):
    """Log errors to file"""
    logging.error(message)
    print(f"❌ API ERROR: {message}")


def call_perplexity_api(prompt, model="sonar"): 
    """
    Call Perplexity API with given prompt
    Returns: API response text or None on failure
    """
    try:
        headers = {
            "Authorization": f"Bearer {config.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a skilled Cameroonian journalist who writes engaging, authentic news content."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = requests.post(config.PERPLEXITY_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
    
    except Exception as e:
        log_error(f"Perplexity API call failed: {str(e)}")
        return None
