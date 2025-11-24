from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime
import config
from news_processor import fetch_news_batch
from logger import log_info, log_success, log_error, console

def start_scheduler():
    """
    Initialize and start the APScheduler with SQLite persistence
    """
    # Setup SQLite job store
    jobstores = {
        'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
    }
    
    scheduler = BlockingScheduler(jobstores=jobstores)
    
    # Add job
    scheduler.add_job(
        fetch_news_batch,
        'interval',
        minutes=config.FETCH_INTERVAL_MINUTES,
        id='news_fetch_job',
        replace_existing=True
    )
    
    console.rule("[bold magenta]🎯 GISTME SCHEDULER[/bold magenta]")
    log_info(f"Fetching news every {config.FETCH_INTERVAL_MINUTES} minutes", module="scheduler")
    log_info(f"Jobs persisted to: jobs.sqlite", module="scheduler")
    log_info(f"Total categories: {len(config.CATEGORIES)}", module="scheduler")
    log_success("Scheduler initialized successfully", module="scheduler")
    console.rule()
    
    # Run first batch immediately
    console.print("\n⚡ [bold yellow]Running first batch immediately...[/bold yellow]\n")
    fetch_news_batch()
    
    # Start scheduler
    try:
        console.print(f"\n🔄 [cyan]Waiting for next batch in {config.FETCH_INTERVAL_MINUTES} minutes...[/cyan]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log_info("Shutdown signal received", module="scheduler")
        console.print("\n👋 [yellow]Shutting down gracefully...[/yellow]")
        scheduler.shutdown()
        log_success("Scheduler stopped cleanly", module="scheduler")
