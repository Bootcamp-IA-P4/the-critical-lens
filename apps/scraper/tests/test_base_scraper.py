# apps/scraper/tests/test_base_scraper.py
import sys
import logging

# Logging configuration basic for the tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from apps.scraper.scrapers.base import BaseScraper

class TestScraper(BaseScraper):
    """A simple test scraper that inherits from BaseScraper."""
    
    def scrape(self):
        """Implementation of the scrape method for testing."""
        # Get a test page (example.com is stable and meant for testing)
        response = self.get_page("https://example.com/")
        soup = self.parse_html(response)
        
        # Extract basic information
        title = soup.title.text
        heading = soup.find('h1').text if soup.find('h1') else "No heading found"
        paragraphs = [p.text for p in soup.find_all('p')]
        
        return {
            'title': title,
            'heading': heading,
            'paragraphs': paragraphs
        }

if __name__ == "__main__":
    print("Testing Base Scraper...")
    
    # Create an instance of our test scraper
    scraper = TestScraper(base_url="https://example.com", name="TestScraper")
    
    try:
        # Execute the scrape method
        result = scraper.scrape()
        
        # Display the results
        print("\nScraping Results:")
        print(f"Title: {result['title']}")
        print(f"Heading: {result['heading']}")
        print(f"Paragraphs: {len(result['paragraphs'])}")
        if result['paragraphs']:
            print(f"First paragraph: {result['paragraphs'][0]}")
        
        print("\nTest completed successfully!")
    except Exception as e:
        print(f"\nTest failed with error: {e}")