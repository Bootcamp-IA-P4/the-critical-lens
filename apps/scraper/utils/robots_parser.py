import urllib.robotparser
import logging
import time
from urllib.parse import urlparse
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class RobotsParser:
    """
    Parser for robots.txt that verifies if access to a URL is allowed.
    
    This class manages downloading and parsing robots.txt files,
    and implements caching to avoid repeated downloads.
    """
    
    def __init__(self, default_user_agent="*"):
        """
        Initialize the robots.txt parser.
        
        Args:
            default_user_agent (str): Default user-agent to use when none is specified.
        """
        self.parsers = {}  # Cache of parsers by domain
        self.default_user_agent = default_user_agent
        self.cache_expiry = 3600  # Cache expiration time in seconds (1 hour)
        self.last_checked = {}  # Record of last check by domain
    
    def _get_base_url(self, url):
        """
        Extract the base URL (scheme + domain) from a complete URL.
        
        Args:
            url (str): URL to analyze
            
        Returns:
            str: Base URL (e.g., 'https://www.example.com')
        """
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    def _fetch_robots_txt(self, base_url):
        """
        Download the robots.txt file for a domain.
        
        Args:
            base_url (str): Base URL of the site (e.g., 'https://www.example.com')
            
        Returns:
            str: Content of the robots.txt file or None if it could not be obtained
        """
        robots_url = f"{base_url}/robots.txt"
        try:
            logger.info(f"Downloading robots.txt from {robots_url}")
            response = requests.get(robots_url, timeout=10)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Could not get robots.txt from {robots_url}. Status code: {response.status_code}")
                return None
        except RequestException as e:
            logger.warning(f"Error downloading robots.txt from {robots_url}: {e}")
            return None
    
    def _create_parser(self, base_url):
        """
        Create a robots.txt parser for a specific domain.
        
        Args:
            base_url (str): Base URL of the site
            
        Returns:
            urllib.robotparser.RobotFileParser: Configured parser or None if it could not be created
        """
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(f"{base_url}/robots.txt")
        
        # Try to get the robots.txt content directly
        robots_content = self._fetch_robots_txt(base_url)
        
        if robots_content:
            # If we get the content, parse it directly
            parser.parse(robots_content.splitlines())
            return parser
        else:
            # If we couldn't get the content, use a permissive parser
            logger.info(f"Could not get robots.txt for {base_url}, assuming access allowed")
            empty_parser = urllib.robotparser.RobotFileParser()
            empty_parser.allow_all = True
            return empty_parser
    
    def can_fetch(self, url, user_agent=None):
        """
        Check if accessing a URL is allowed according to robots.txt.
        
        Args:
            url (str): Complete URL to verify
            user_agent (str, optional): User-agent for verification.
                                      If None, the default_user_agent is used.
            
        Returns:
            bool: True if access is allowed, False otherwise
        """
        if user_agent is None:
            user_agent = self.default_user_agent
            
        base_url = self._get_base_url(url)
        
        # Check if we need to create or update the parser for this domain
        current_time = time.time()
        if (base_url not in self.parsers or 
            base_url not in self.last_checked or 
            current_time - self.last_checked[base_url] > self.cache_expiry):
            
            # Create or update the parser
            self.parsers[base_url] = self._create_parser(base_url)
            self.last_checked[base_url] = current_time
        
        # Check if access is allowed
        parser = self.parsers[base_url]
        if parser.allow_all:
            return True
            
        can_access = parser.can_fetch(user_agent, url)
        logger.debug(f"Robots.txt verification for {url} with user-agent '{user_agent}': {'allowed' if can_access else 'not allowed'}")
        
        return can_access