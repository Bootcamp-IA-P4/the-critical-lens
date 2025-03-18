import logging
import time
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from .base import BaseScraper

logger = logging.getLogger(__name__)

class NewtralScraper(BaseScraper):
    """
    Specialized scraper for extracting fact-checks from Newtral.
    Uses Selenium for navigation and BeautifulSoup for parsing content.
    """
    def __init__(self):
        """Initialize the Newtral scraper with the base URL."""
        super().__init__(
            base_url="https://www.newtral.es",
            name="NewtralScraper"
        )
        self.fact_check_url = "https://www.newtral.es/zona-verificacion/fact-check/"

    def _initialize_webdriver(self):
        """Initialize and configure the Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # Add the current User-Agent to maintain consistency
        chrome_options.add_argument(f"user-agent={self.session.headers['User-Agent']}")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def _clean_text(self, text):
        """
        Clean text by removing unwanted content.
        
        Args:
            text (str): Text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
            
        # Patterns to remove
        cleanup_patterns = [
            r"Con tu consentimiento, nosotros y\s+nuestros \d+ socios usamos cookies.*?servicios",
            r"Almacenar la información en un dispositivo.*?procesamiento de datos",
            r"Puedes retirar tu consentimiento.*?servicios",
            r"Nosotros y nuestros socios hacemos el siguiente tratamiento de datos:.*"
        ]
        
        # Remove cookie patterns and unwanted text
        for pattern in cleanup_patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL|re.IGNORECASE)
            
        # Remove extra spaces, line breaks and normalize
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _extract_claim(self, soup):
        """
        Extract the claim from the article.
        
        Args:
            soup (BeautifulSoup): Parsed BeautifulSoup object
            
        Returns:
            str: Extracted claim or None
        """
        # Selectors to find the claim
        claim_selectors = [
            # Quoted or marked text
            'blockquote',
            "span[style*='background-color']",
            "mark",
            "strong",
            
            # Newtral-specific selectors
            "span.card-text-marked-pistachiomark",
            "div.claim p",
            "blockquote.claim",
            ".card-text-marked-orange",  # Add this specific selector
            ".card-text-container .card-text-marked-orange mark",  # More specific selector
            
            # Paragraphs with distinctive text
            "p.single-main-contentfactchecks-methodology-result",
            
            # Main content
            "div.article-content p:first-of-type",
            "p.destacado"
        ]
        
        for selector in claim_selectors:
            claim_elements = soup.select(selector)
            
            for element in claim_elements:
                claim_text = element.get_text(strip=True)
                
                # Clean quotes and extra spaces
                claim_text = re.sub(r'^["""]|["""]$', '', claim_text)  # Fix the regular expression
                claim_text = re.sub(r'\s+', ' ', claim_text).strip()
                
                # Validate length and relevance of the claim
                if claim_text and 20 <= len(claim_text) <= 500:
                    return claim_text
                    
        return None

    def _extract_claim_source(self, soup):
        """
        Extract the source of the claim from the article.
        
        Args:
            soup (BeautifulSoup): Parsed BeautifulSoup object
            
        Returns:
            str: Source of the claim or None
        """
        # Look in the author card section
        author_element = soup.select_one('.card-author-text-link')
        if author_element:
            return author_element.get_text(strip=True)
            
        # Look in other possible places
        source_elements = soup.select('.card-author-text span')
        if source_elements and len(source_elements) > 1:
            return source_elements[0].get_text(strip=True)
            
        # Try to extract from the first paragraph of content
        first_paragraph = soup.select_one('.section-post-content p')
        if first_paragraph:
            text = first_paragraph.get_text(strip=True)
            # Look for common patterns to identify the source
            patterns = [
                r'([\w\s]+) (dijo|afirmó|aseguró|declaró)',
                r'([\w\s]+), (dijo|afirmó|aseguró|declaró)',
                r'según ([\w\s]+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
                    
        return None

    def _extract_tags(self, soup):
        """
        Extract tags from the article.
        
        Args:
            soup (BeautifulSoup): Parsed BeautifulSoup object
            
        Returns:
            list: List of extracted tags
        """
        tags = []
        
        # Look in the tags section
        tag_section = soup.select_one('.section-post-tags')
        if tag_section:
            tag_elements = tag_section.select('.pill-outline')
            for tag_element in tag_elements:
                tag_text = tag_element.get_text(strip=True)
                if tag_text:
                    tags.append(tag_text)
                    
        return tags

    def _extract_author(self, soup):
        """
        Extract the author of the article.
        
        Args:
            soup (BeautifulSoup): Parsed BeautifulSoup object
            
        Returns:
            str: Author's name or None
        """
        # Selectors to find the author
        author_selectors = [
            # Specific author selectors
            "div.author-name",
            "span.author-name",
            "meta[name='author']",
            ".post-author a",
            "a.author-link",
            
            # Other general options
            "p.byline",
            "span.byline-author",
            ".article-author"
        ]
        
        for selector in author_selectors:
            author_elements = soup.select(selector)
            
            for element in author_elements:
                # Get author text
                author_text = element.get_text(strip=True)
                
                # Clean "Por " text and dates
                author_text = re.sub(r'^Por\s+', '', author_text, flags=re.IGNORECASE)
                author_text = re.sub(r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}', '', author_text)
                author_text = re.sub(r'\s+', ' ', author_text).strip()
                
                # Validate name length
                if author_text and 2 <= len(author_text) <= 100:
                    return author_text
                    
        return None

    def _extract_content(self, soup):
        """
        Extract the main content of the article.
        
        Args:
            soup (BeautifulSoup): Parsed BeautifulSoup object
            
        Returns:
            str: Extracted content or None
        """
        # Selectors to find the main content
        content_selectors = [
            "div.entry-content",
            "div.article-content",
            "div.post-content",
            "article.post-content",
            "div.main-content",
            "div.content"
        ]
        
        # Keywords to identify relevant paragraphs
        relevant_keywords = [
            'según', 'afirma', 'señala', 'datos', 'evidencia', 'verificación',
            'análisis', 'investigación', 'fuente', 'demostrado', 'resultado'
        ]
        
        # Try to extract content with different strategies
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # Extract all paragraphs
                paragraphs = content_element.find_all('p')
                
                # Clean and filter paragraphs
                cleaned_paragraphs = []
                for p in paragraphs:
                    text = self._clean_text(p.get_text())
                    
                    # Filter paragraphs
                    if (text and
                        len(text) > 50 and
                        'cookies' not in text.lower() and
                        not text.startswith('Con tu consentimiento')):
                        
                        # Prioritize paragraphs with relevant keywords
                        if any(keyword in text.lower() for keyword in relevant_keywords):
                            cleaned_paragraphs.insert(0, text)
                        else:
                            cleaned_paragraphs.append(text)
                            
                # Join paragraphs
                content_text = ' '.join(cleaned_paragraphs)
                
                # Validate content length
                if len(content_text) > 100:
                    return content_text
                    
        # Fallback strategy: extract text from all paragraphs in the document
        all_paragraphs = soup.find_all('p')
        fallback_paragraphs = []
        
        for p in all_paragraphs:
            text = self._clean_text(p.get_text())
            if (text and
                len(text) > 50 and
                'cookies' not in text.lower() and
                not text.startswith('Con tu consentimiento')):
                fallback_paragraphs.append(text)
                
        # Try to join fallback paragraphs
        fallback_content = ' '.join(fallback_paragraphs)
        return fallback_content if len(fallback_content) > 100 else None

    def _get_fact_check_urls(self, limit):
        """
        Extract URLs of fact-check articles.
        
        Args:
            limit (int): Maximum number of URLs to extract
            
        Returns:
            list: List of fact-check URLs
        """
        logger.info(f"Extracting up to {limit} fact-check URLs")
        
        # Predefined URLs as fallback
        predefined_urls = [
            "https://www.newtral.es/espana-ayuda-militar-ucrania-factcheck/20250317/",
            "https://www.newtral.es/presion-fiscal-patxi-lopez-factcheck/20250312/",
            "https://www.newtral.es/mujeres-autonomas-madrid-factcheck/20250310/"
        ]

        # Initialize WebDriver
        driver = self._initialize_webdriver()
        
        try:
            # Open the fact-checks page
            driver.get(self.fact_check_url)
            
            # Wait for elements to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article.item, h2 a"))
            )
            
            # More robust URL extraction strategy
            urls = []
            page_height = driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            
            while len(urls) < limit and scroll_attempts < 10:
                # Look for specific fact-check URL selectors
                url_selectors = [
                    "article.item a[href*='factcheck']",
                    "h2 a[href*='factcheck']",
                    "div.post-list a[href*='factcheck']",
                    "a.post-link[href*='factcheck']"
                ]
                
                for selector in url_selectors:
                    try:
                        article_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in article_elements:
                            url = element.get_attribute('href')
                            if (url and
                                '/factcheck/' in url.lower() and
                                url not in urls and
                                re.search(r'/202\d{5}/', url)):
                                urls.append(url)
                                
                            if len(urls) >= limit:
                                break
                                
                        if len(urls) >= limit:
                            break
                    except Exception as e:
                        logger.warning(f"Error with selector {selector}: {e}")
                        
                # If not enough URLs, scroll down
                if len(urls) < limit:
                    # Scroll to the bottom of the page
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Wait for more content to load
                    
                    # Check if page height has changed
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == page_height:
                        scroll_attempts += 1
                    else:
                        page_height = new_height
                        scroll_attempts = 0
                        
            # If no URLs found, use predefined ones
            if not urls:
                urls = predefined_urls
                
            logger.info(f"Found {len(urls)} fact-check URLs")
            return urls[:limit]
            
        except Exception as e:
            logger.error(f"Error extracting fact-check URLs: {e}")
            return predefined_urls[:limit]
            
        finally:
            # Close the WebDriver
            driver.quit()

    def scrape(self, **kwargs):
        """
        Main method to extract fact-checks from Newtral.
        
        Args:
            **kwargs: Keyword arguments (such as 'limit')
            
        Returns:
            list: List of extracted articles
        """
        # Get extraction limit, default 10
        limit = kwargs.get('limit', 10)
        logger.info(f"Starting to extract fact-checks from Newtral. Limit: {limit}")
        
        # Get fact-check URLs
        article_urls = self._get_fact_check_urls(limit)
        
        # Extract each article
        articles = []
        for url in article_urls:
            try:
                article = self._scrape_fact_check_article(url)
                if article:
                    articles.append(article)
                    logger.info(f"Article successfully extracted: {article.get('title', 'No title')}")
            except Exception as e:
                logger.error(f"Error extracting article {url}: {e}")
                
        logger.info(f"Extraction completed. {len(articles)} articles extracted")
        return articles

    def _scrape_fact_check_article(self, url):
        """
        Extract an individual fact-check article.
        
        Args:
            url (str): URL of the article to extract
            
        Returns:
            dict: Extracted article data
        """
        logger.info(f"Extracting fact-check article: {url}")
        
        # Initialize WebDriver
        driver = self._initialize_webdriver()
        
        try:
            # Navigate to the URL
            driver.get(url)
            
            # Wait for main content to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1, .post-title, .article-content"))
            )
            
            # Get the page HTML
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title_selectors = [
                "h1.post-title",
                "h1",
                ".article-title",
                "header h1",
                ".entry-title"
            ]
            
            title = None
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title = self._clean_text(title_element.get_text())
                    break
                    
            # Extract verification
            verification_categories = ["Verdad a medias", "Falso", "Engañoso", "Verdadero"]
            category = None
            
            # Look for category in different elements
            for cat in verification_categories:
                # Look for direct text
                category_elements = soup.find_all(string=lambda text: cat in text)
                
                # Look in elements with specific style or class
                if not category_elements:
                    category_elements = soup.select(f"*:contains('{cat}')")
                    
                if category_elements:
                    category = cat
                    break
                    
            # Extract date from URL or page
            publish_date = None
            try:
                # First try to extract from URL
                url_match = re.search(r'/(\d{8})/', url)
                if url_match:
                    date_str = url_match.group(1)
                    publish_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    
                # If that fails, try to extract from the page
                if not publish_date:
                    date_selectors = [
                        "time[datetime]",
                        ".post-date",
                        ".entry-date",
                        "meta[property='article:published_time']"
                    ]
                    
                    for selector in date_selectors:
                        date_element = soup.select_one(selector)
                        if date_element:
                            # Extract date from different attributes
                            if selector == "meta[property='article:published_time']":
                                date_str = date_element.get('content', '')
                            else:
                                date_str = date_element.get_text(strip=True)
                                
                            # Try to parse different date formats
                            try:
                                # ISO format
                                parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                publish_date = parsed_date.strftime("%Y-%m-%d")
                                break
                            except:
                                # Spanish format
                                months_dict = {
                                    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
                                    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
                                    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
                                }
                                
                                match = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', date_str.lower())
                                if match:
                                    day, month_name, year = match.groups()
                                    if month_name in months_dict:
                                        publish_date = f"{year}-{months_dict[month_name]}-{day.zfill(2)}"
                                        break
            except Exception as e:
                logger.warning(f"Error extracting date: {e}")
                
            # Extract content
            content = self._extract_content(soup)
            
            # Extract claim
            claim = self._extract_claim(soup)
            
            # Extract claim source
            claim_source = self._extract_claim_source(soup)
            
            # Extract image
            image_selectors = [
                "img.featured-image",
                "figure img",
                "div.main-image img",
                "img.post-thumbnail",
                "meta[property='og:image']",
                ".wp-post-image"
            ]
            
            image_url = None
            for selector in image_selectors:
                image_element = soup.select_one(selector)
                if image_element:
                    # Get image URL from different attributes
                    if selector == "meta[property='og:image']":
                        image_url = image_element.get('content')
                    else:
                        image_url = (image_element.get('src') or
                                    image_element.get('data-src') or
                                    image_element.get('data-original'))
                                    
                    # Validate and normalize image URL
                    if image_url:
                        # Convert relative URLs to absolute
                        if image_url.startswith('//'):
                            image_url = 'https:' + image_url
                        elif image_url.startswith('/'):
                            image_url = f"{self.base_url.rstrip('/')}{image_url}"
                            
                        # Verify it's a valid URL
                        if image_url.startswith('http'):
                            break
                            
            # Extract tags
            tags = self._extract_tags(soup)
            
            # Extract author
            author = self._extract_author(soup)
            
            # Build article dictionary
            article = {
                "title": title,
                "url": url,
                "verification_category": category,
                "publish_date": publish_date,
                "claim": claim,
                "claim_source": claim_source,
                "content": content,
                "tags": tags,
                "image_url": image_url,
                "author": author,
                "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Log extracted data
            logger.info(f"Data extracted from article: {article}")
            
            return article
            
        except Exception as e:
            logger.error(f"Error extracting article {url}: {e}")
            return None
            
        finally:
            # Close the WebDriver
            try:
                driver.quit()
            except Exception as quit_error:
                logger.warning(f"Error closing WebDriver: {quit_error}")
