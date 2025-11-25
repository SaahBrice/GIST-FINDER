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
    # Ensure table exists. New schema stores both English and French headlines.
    conn.execute("""CREATE TABLE IF NOT EXISTS seen_articles (
        id INTEGER PRIMARY KEY,
        headline_en TEXT,
        headline_fr TEXT,
        content_hash TEXT,
        category TEXT,
        created_at DATETIME,
        source TEXT
    )""")

    # Migrate legacy schema if needed: older versions stored a single `headline` column.
    cur = conn.execute("PRAGMA table_info('seen_articles')")
    cols = [row[1] for row in cur]
    if 'headline' in cols and ('headline_en' not in cols or 'headline_fr' not in cols):
        try:
            # Add new columns if missing
            if 'headline_en' not in cols:
                conn.execute("ALTER TABLE seen_articles ADD COLUMN headline_en TEXT")
            if 'headline_fr' not in cols:
                conn.execute("ALTER TABLE seen_articles ADD COLUMN headline_fr TEXT")
            # Copy legacy headline into both new columns to preserve behavior
            conn.execute("UPDATE seen_articles SET headline_en = headline WHERE headline_en IS NULL")
            conn.execute("UPDATE seen_articles SET headline_fr = headline WHERE headline_fr IS NULL")
            conn.commit()
            log_info("Migrated legacy `seen_articles` headline column into bilingual columns", module='deduplication')
        except Exception:
            # If migration fails, ignore and continue - queries will still work for new rows
            pass
    return conn

def hash_text(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def is_duplicate(new_headline_en, new_headline_fr, category, allowed_similarity, max_hours):
    """
    Compare incoming bilingual headlines against recent stored headlines.
    Checks English vs English, French vs French and cross-language combinations.
    """
    conn = get_db()
    cutoff_time = datetime.utcnow() - timedelta(hours=max_hours)
    cur = conn.execute("""SELECT headline_en, headline_fr, created_at FROM seen_articles
                          WHERE category=? AND created_at > ?""", (category, cutoff_time.isoformat()))
    for old_en, old_fr, created_at in cur:
        # compare english-to-english
        if old_en and new_headline_en:
            similarity = fuzz.ratio(new_headline_en.lower(), old_en.lower())
            if similarity >= allowed_similarity:
                log_warning(f"Duplicate blocked (similarity {similarity}%): {new_headline_en[:50]}...", module='deduplication')
                conn.close()
                return True
        # compare french-to-french
        if old_fr and new_headline_fr:
            similarity = fuzz.ratio(new_headline_fr.lower(), old_fr.lower())
            if similarity >= allowed_similarity:
                log_warning(f"Duplicate blocked (similarity {similarity}%): {new_headline_fr[:50]}...", module='deduplication')
                conn.close()
                return True
        # cross-language comparisons (sometimes same idea phrased different languages)
        if old_en and new_headline_fr:
            similarity = fuzz.ratio(new_headline_fr.lower(), old_en.lower())
            if similarity >= allowed_similarity:
                log_warning(f"Duplicate blocked (cross-lang similarity {similarity}%): {new_headline_fr[:50]}...", module='deduplication')
                conn.close()
                return True
        if old_fr and new_headline_en:
            similarity = fuzz.ratio(new_headline_en.lower(), old_fr.lower())
            if similarity >= allowed_similarity:
                log_warning(f"Duplicate blocked (cross-lang similarity {similarity}%): {new_headline_en[:50]}...", module='deduplication')
                conn.close()
                return True
    conn.close()
    return False

def save_article(headline_en, headline_fr, category, source):
    conn = get_db()
    # Hash combined text to detect duplicates at content level if needed
    combined = (headline_en or '') + '||' + (headline_fr or '')
    h = hash_text(combined)
    now = datetime.utcnow().isoformat()
    try:
        conn.execute("""INSERT INTO seen_articles (headline_en, headline_fr, content_hash, category, created_at, source)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (headline_en, headline_fr, h, category, now, source))
        conn.commit()
        log_success(f"Stored headlines: EN:{(headline_en or '')[:50]} | FR:{(headline_fr or '')[:50]}...", module='deduplication')
    except sqlite3.IntegrityError:
        log_warning(f"Already seen: EN:{(headline_en or '')[:50]} | FR:{(headline_fr or '')[:50]}...", module='deduplication')
    conn.close()
