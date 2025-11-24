import os
from dotenv import load_dotenv
import random

load_dotenv()

# API Configuration
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions'

# Scheduling
FETCH_INTERVAL_MINUTES = 30

# News Categories - Comprehensive list
CATEGORIES = [
    'politics',
    'sports', 
    'entertainment',
    'business',
    'technology',
    'health',
    'education',
    'agriculture',
    'culture',
    'crime',
    'environment',
    'international',
    'economy',
    'society',
    'human_interest',
    'lifestyle',
    'religion',
    'transportation',
    'real_estate',
    'science'
    'concours_launch',         # HOT GIST New specialized category
    'exam_results'             # HOT GIST New specialized category
    'latest_jobs'             #  HOT GIST New specialized category
]

# File Paths
AUDIO_DIR_FRENCH = 'media/audio/french'
AUDIO_DIR_ENGLISH = 'media/audio/english'
THUMBNAIL_DIR = 'media/thumbnails'
LOG_FILE = 'logs/errors.log'

# Content Settings - Randomized word count
SUMMARY_WORD_OPTIONS = [200, 400, 600, 800, 1000]  # Steps of 200

def get_random_word_count():
    '''Returns a random word count from the options'''
    return random.choice(SUMMARY_WORD_OPTIONS)
