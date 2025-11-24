import time
import threading
from uploader import retry_failed_uploads
from logger import log_info

def run_retry_scheduler(interval_seconds=3600):
    """
    Run retry_failed_uploads() every `interval_seconds` seconds in background.
    """
    def scheduler_loop():
        while True:
            log_info("Starting retry of failed uploads...")
            retry_failed_uploads()
            log_info(f"Retry cycle complete. Next retry in {interval_seconds} seconds.")
            time.sleep(interval_seconds)
    
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
    log_info(f"Retry scheduler started, running every {interval_seconds} seconds.")

if __name__ == "__main__":
    run_retry_scheduler()
    # Keep main thread alive so scheduler thread keeps running
    while True:
        time.sleep(60)
