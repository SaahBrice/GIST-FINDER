import sqlite3
import hashlib
from datetime import datetime, timedelta
from rapidfuzz import fuzz
from logger import log_info, log_success, log_warning

DB_FILE = 'deduplication.sqlite'

#how long can we say an article is "recent" (in hours) and different from what we have seen before
max_hours = 72
#what is the allowed similarity percentage to consider two headlines as duplicates
allowed_similarity = 60

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""CREATE TABLE IF NOT EXISTS seen_articles (
        id INTEGER PRIMARY KEY,
        headline TEXT,
        content_hash TEXT,
        category TEXT,
        created_at DATETIME,
        source TEXT
    )""")
    return conn

def hash_text(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def is_duplicate(new_headline, category, allowed_similarity, max_hours):
    conn = get_db()
    cutoff_time = datetime.utcnow() - timedelta(hours=max_hours)
    # Fetch only recent articles in the same category
    cur = conn.execute("""SELECT headline, created_at FROM seen_articles
                          WHERE category=? AND created_at > ?""", (category, cutoff_time.isoformat()))
    for old_headline, created_at in cur:
        similarity = fuzz.ratio(new_headline.lower(), old_headline.lower())
        if similarity >= allowed_similarity:
            log_warning(f"Duplicate blocked (similarity {similarity}%): {new_headline[:50]}...", module='deduplication')
            conn.close()
            return True
    conn.close()
    return False

def save_article(headline, category, source):
    conn = get_db()
    h = hash_text(headline)
    now = datetime.utcnow().isoformat()
    try:
        conn.execute("""INSERT INTO seen_articles (headline, content_hash, category, created_at, source)
                        VALUES (?, ?, ?, ?, ?)""",
                        (headline, h, category, now, source))
        conn.commit()
        log_success(f"Stored headline: {headline[:50]}...", module='deduplication')
    except sqlite3.IntegrityError:
        log_warning(f"Already seen: {headline[:50]}...", module='deduplication')
    conn.close()
