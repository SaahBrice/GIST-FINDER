#!/usr/bin/env python3
"""
GistMe News Automation Pipeline
Main entry point for the news automation system
"""

from scheduler import start_scheduler
from logger import console, log_info
import sys

def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          GISTME NEWS AUTOMATION PIPELINE                 ║
║                                                          ║
║  🇨🇲  Cameroonian News | Dual Language | Audio-First   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

def main():
    """Main function - starts the entire pipeline"""
    try:
        print_banner()
        log_info("Pipeline starting up...", module="main")
        
        # Start the scheduler (blocks and runs continuously)
        start_scheduler()
        
    except Exception as e:
        console.print(f"\n💥 [bold red]Fatal error:[/bold red] {e}")
        log_info(f"Fatal error: {e}", module="main")
        sys.exit(1)

if __name__ == "__main__":
    main()
