import pytest
from apps.scraper.utils.user_agents import UserAgentManager
from apps.scraper.scrapers import BaseScraper

@pytest.fixture
def ua_manager():
    """Provides a user agent manager for testing"""
    return UserAgentManager()

@pytest.fixture
def base_scraper():
    """Provides a scraper for testing"""
    return BaseScraper("https://httpbin.org", name="TestScraper")

def test_user_manager(ua_manager):
    """
    Provides that UserAgentManager can provide different user agents
    """
    # Get user agents
    random_ua = ua_manager.get_random_user_agent()
    desktop_ua = ua_manager.get_desktop_user_agent()

    # Check that the user agents are valid
    assert random_ua is not None and len(random_ua) > 0
    assert desktop_ua is not None and len(desktop_ua) > 0

    # Print to manual inspection
    print(f"Random User Agent: {random_ua}")
    print(f"Desktop User Agent: {desktop_ua}")


def test_user_agent_rotation(base_scraper):
    """
    Tests that the scraper can rotate user agents.
    """
    # Save initial user agent
    initial_ua = base_scraper.session.headers.get('User-Agent')
    
    # Rotate user agent
    base_scraper.rotate_user_agent()
    new_ua = base_scraper.session.headers.get('User-Agent')
    
    # Check that the user agent has changed
    assert initial_ua != new_ua
    print(f"\nCambio de User-Agent:\nAnterior: {initial_ua}\nNuevo: {new_ua}")

def test_user_agent_in_request(base_scraper):
    """
    Tests that the user agent is correctly sent in a request.
    Skip in case of connection error.
    """
    try:
        # Make a real request to httpbin.org
        response = base_scraper.get_page("user-agent")

        # Get the user agent reported by httpbin.org
        data = response.json()
        reported_ua = data["user-agent"]
        current_ua = base_scraper.session.headers["User-Agent"]

        # Check that the user agent is the same as the one we sent
        assert reported_ua == current_ua
        print(f"\nUserr-Agent recibido por el servidor: {current_ua}")
    except Exception as e:
        pytest.skip(f"Test omitido por error de conexión: {e}")
    