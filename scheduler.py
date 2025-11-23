import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime
import config
from news_processor import fetch_news_batch


# Setup logging
logging.basicConfig(
    filename=config.LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def start_scheduler():
    """
    Initialize and start the APScheduler with SQLite persistence
    Runs the news fetching job at configured intervals
    """
    # Setup SQLite job store for persistence
    jobstores = {
        'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
    }
    
    scheduler = BlockingScheduler(jobstores=jobstores)
    
    # Add job to run every X minutes
    scheduler.add_job(
        fetch_news_batch,
        'interval',
        minutes=config.FETCH_INTERVAL_MINUTES,
        id='news_fetch_job',
        replace_existing=True
    )
    
    print(f"🎯 GistMe News Pipeline Started!")
    print(f"📅 Fetching news every {config.FETCH_INTERVAL_MINUTES} minutes")
    print(f"💾 Jobs persisted to: jobs.sqlite")
    print(f"📂 Categories: {len(config.CATEGORIES)} total")
    print(f"🔄 Press Ctrl+C to stop\n")
    
    # Run once immediately on startup
    print("⚡ Running first batch immediately...\n")
    fetch_news_batch()
    
    # Start scheduler
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Shutting down gracefully...")
        scheduler.shutdown()
