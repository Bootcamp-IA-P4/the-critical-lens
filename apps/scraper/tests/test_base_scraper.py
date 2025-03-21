import pytest
from apps.scraper.scrapers.base import BaseScraper

class ScraperForTest(BaseScraper):
    """Test scraper that inherits from BaseScraper."""
    
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

@pytest.fixture
def scraper():
    """Fixture to provide a TestScraper instance."""
    return ScraperForTest(base_url="https://example.com/", name="TestScraper")

def test_scraper_scrape(scraper):
    """Test for the basic functionality of the scraper.
    
    Args:
        scraper: Fixture providing a TestScraper instance.
    """
    # Test the scrape method
    result = scraper.scrape()
    
    # Check if the result contains the expected keys
    assert 'title' in result
    assert 'heading' in result
    assert 'paragraphs' in result
    assert "Example Domain" in result['title']
    assert len(result['paragraphs']) > 0
