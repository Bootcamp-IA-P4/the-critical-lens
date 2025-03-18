# apps/scraper/utils/user_agents.py
import logging
import random
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class UserAgentManager:
    """
    Manages a collection of user agents for web scraping to help avoid detection.
    
    This class provides methods to get random user agents and rotate between them.
    """
    
    def __init__(self):
        """Initialize the user agent manager with a UserAgent instance and fallbacks."""
        # Fallback user agents in case UserAgent() fails
        self.fallback_user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        ]
        
        # Try to initialize fake_useragent, with graceful fallback
        try:
            self.ua = UserAgent()
            self.use_library = True
            logger.info("UserAgent library initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize UserAgent library: {e}. Using fallback user agents.")
            self.use_library = False
    
    def get_random_user_agent(self):
        """Get a random user agent string."""
        if self.use_library:
            try:
                return self.ua.random
            except Exception as e:
                logger.warning(f"Error getting random user agent from library: {e}. Using fallback.")
                
        # Use fallback if library fails or isn't available
        return random.choice(self.fallback_user_agents)
    
    def get_desktop_user_agent(self):
        """Get a user agent for desktop browsers."""
        if self.use_library:
            try:
                agents = [self.ua.chrome, self.ua.firefox, self.ua.edge, self.ua.safari]
                return random.choice([agent for agent in agents if callable(agent)])()
            except Exception as e:
                logger.warning(f"Error getting desktop user agent: {e}. Using fallback.")
        
        # Use desktop-specific fallback agents
        desktop_agents = [ua for ua in self.fallback_user_agents if 'Mobile' not in ua]
        return random.choice(desktop_agents or self.fallback_user_agents)