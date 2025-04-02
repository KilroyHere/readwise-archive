"""
Package for news source scrapers.
"""

from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """Base class for news source scrapers."""
    
    def __init__(self, output_path=None):
        """
        Initialize the scraper.
        
        Args:
            output_path (str, optional): Directory to save output files.
        """
        self.output_path = output_path
    
    @abstractmethod
    def scrape(self):
        """
        Scrape articles from the news source.
        
        Returns:
            list: List of article URLs.
        """
        pass

# Import specific scrapers
from news_archiver.scrapers.atlantic import AtlanticScraper
from news_archiver.scrapers.economist import EconomistScraper

# Dictionary mapping source names to scraper classes
SCRAPERS = {
    'atlantic': AtlanticScraper,
    'economist': EconomistScraper
} 