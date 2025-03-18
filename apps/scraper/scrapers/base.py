import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class BaseScraper:
  """
  Base class for all scrapers implements common scraping functionality.

  This class provides basic methods for making HTTP request and parsing HTML.
  """

  def __init__(self, base_url, name="BaseScraper"):
    """
    Initialize the base scraper with configuration.

    Args:
      base_url (str): The base URL of the website to scrape.
      name (str): A name for this scraper for logging purposes.
    """
    self.base_url = base_url
    self.name = name
    self.session = requests.Session()

    # Configure default headers
    self.session.headers.update({
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9, */*;q=0.8',
    })

    logger.info(f"Initialized {self.name} scraper for {base_url}")

    def get_page(self, url, timeout=30):
      """
      Get a web page.

      Args:
        url (str): The URL to fetch
        timeout (int): Request timeout in seconds

      Returns:
          requests.Response: The response object if successful
      """
      full_url = url if url.startswith('http') else f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"

      logger.info(f"Fetching URL: {full_url}")
      response = self.session.get(full_url, timeout=timeout)
      response.raise_for_status()
      return response
    
    def parse_html(self, response):
      """
      Parse HTML response with BeautifulSoup.

      Args:
        response (requests.Response): The response object

      Returns:
        BeautifulSoup: The parsed HTML
      """
      return BeautifulSoup(response.text, 'html.parser')

      def scrape(self):
        """
        Main scraping method to be implemented by subclasses.

        Raises:
        NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the scrape() method")