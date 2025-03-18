import logging
import requests
from bs4 import BeautifulSoup
import time
import random
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class BaseScraper:
    """
    Base class for all scrapers that implements common scraping functionality.

    This class provides basic methods for making HTTP requests and parsing HTML.
    """

    def __init__(self, base_url, name="BaseScraper", max_retries=3, retry_delay=2):
        """
        Initialize the base scraper with configuration.

        Args:
            base_url (str): The base URL of the website to scrape.
            name (str): A name for this scraper for logging purposes.
            max_retries (int): Number of retry attempts in case of request failure.
            retry_delay (int): Base delay in seconds between retries.
        """
        self.base_url = base_url
        self.name = name
        self.session = requests.Session()
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Configure default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })

        logger.info(f"Initialized {self.name} scraper for {base_url}")

    def get_page(self, url, timeout=30):
        """
        Get a web page.

        Args:
            url (str): The URL to fetch.
            timeout (int): Request timeout in seconds.

        Returns:
            requests.Response: The response object if successful.
        """
        full_url = url if url.startswith('http') else f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"

        for attempt in range(self.max_retries):
            try:
                # Add a delay for retries
                if attempt > 0:
                    delay = self.retry_delay * (1 + random.random())
                    logger.debug(f"Retry attempt {attempt+1}/{self.max_retries}. Waiting {delay:.2f}s before retry.")
                    time.sleep(delay)
                
                # Make the request
                logger.info(f"Fetching URL: {full_url}")
                response = self.session.get(full_url, timeout=timeout)

                # Check if the request was successful
                response.raise_for_status()
                return response

            except RequestException as e:
                logger.warning(f"Error fetching URL: {full_url}. Error: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to fetch {full_url} after {self.max_retries} attempts")
                    raise
        
        raise Exception(f"Failed to fetch {full_url} after {self.max_retries} attempts")

    def parse_html(self, response):
        """
        Parse HTML response with BeautifulSoup.

        Args:
            response (requests.Response): The response object.

        Returns:
            BeautifulSoup: The parsed HTML.
        """
        return BeautifulSoup(response.text, 'html.parser')

    def scrape(self):
        """
        Main scraping method to be implemented by subclasses.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the scrape() method")
