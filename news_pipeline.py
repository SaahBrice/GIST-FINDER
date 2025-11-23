#!/usr/bin/env python3
"""
GistMe News Automation Pipeline
Main entry point for the news automation system
"""

from scheduler import start_scheduler


def main():
    """
    Main function - starts the entire pipeline
    """
    print("="*60)
    print("          GISTME NEWS AUTOMATION PIPELINE")
    print("="*60)
    print("🇨🇲 Cameroonian News | Dual Language | Audio-First")
    print("="*60)
    print()
    
    # Start the scheduler (this blocks and runs continuously)
    start_scheduler()


if __name__ == "__main__":
    main()
