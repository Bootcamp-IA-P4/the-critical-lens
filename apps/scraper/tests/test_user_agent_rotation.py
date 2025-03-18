# apps/scraper/tests/test_user_agent_rotation.py
import os
import sys
import logging

# Importation paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.insert(0, project_root)

from apps.scraper.utils.logging_config import configure_logging
from apps.scraper.utils.user_agents import UserAgentManager
from apps.scraper.scrapers import BaseScraper

def test_user_agent_rotation():
    """Test the user agent rotation functionality."""
    print("Testing user agent rotation...")
    
    # Configure logging
    configure_logging(log_level=logging.INFO)
    
    # Test UserAgentManager directly
    ua_manager = UserAgentManager()
    print("\nTesting UserAgentManager:")
    print(f"Random user agent: {ua_manager.get_random_user_agent()}")
    print(f"Desktop user agent: {ua_manager.get_desktop_user_agent()}")
    
    # Test user agent rotation in BaseScraper
    scraper = BaseScraper("https://httpbin.org", name="UARotationTester")
    
    print("\nTesting BaseScraper user agent rotation:")
    
    # Get current user agent
    current_ua = scraper.session.headers.get('User-Agent')
    print(f"Initial User-Agent: {current_ua}")
    
    # Rotate and get new user agent
    scraper.rotate_user_agent()
    new_ua = scraper.session.headers.get('User-Agent')
    print(f"After rotation: {new_ua}")
    
    # Verify that user agent changed
    print(f"User agent changed: {current_ua != new_ua}")
    
    # Test with a real request to httpbin.org/user-agent which returns the user agent
    try:
        print("\nMaking a test request to httpbin.org/user-agent:")
        response = scraper.get_page("user-agent")
        data = response.json()
        print(f"User agent received by server: {data.get('user-agent')}")
        print(f"Matches current UA: {data.get('user-agent') == scraper.session.headers.get('User-Agent')}")
    except Exception as e:
        print(f"Error making test request: {e}")
    
    print("\nUser agent rotation test completed")

if __name__ == "__main__":
    test_user_agent_rotation()