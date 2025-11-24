import requests
import config
from logger import log_error, log_info

def call_perplexity_api(prompt, model="sonar"):
    """
    Call Perplexity API with given prompt
    Returns: API response text or None on failure
    """
    try:
        log_info(f"Calling Perplexity API ({model})...", module="api_client")
        
        headers = {
            "Authorization": f"Bearer {config.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = requests.post(config.PERPLEXITY_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()['choices'][0]['message']['content']
        log_info(f"API call successful ({len(result)} chars)", module="api_client")
        return result
    
    except Exception as e:
        log_error(f"Perplexity API call failed: {str(e)}", module="api_client")
        return None
