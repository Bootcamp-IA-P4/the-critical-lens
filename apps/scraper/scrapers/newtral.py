import logging
import time
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from contextlib import contextmanager

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

# Constantes y configuración
BASE_URL = "https://www.newtral.es"
FACT_CHECK_URL = f"{BASE_URL}/zona-verificacion/fact-check/"
DEFAULT_TIMEOUT = 30
LOAD_MORE_WAIT = 3
CLEANUP_PATTERNS = [
    r"Con tu consentimiento, nosotros y\s+nuestros \d+ socios usamos cookies.*?servicios",
    r"Almacenar la información en un dispositivo.*?procesamiento de datos",
    r"Puedes retirar tu consentimiento.*?servicios",
    r"Nosotros y nuestros socios hacemos el siguiente tratamiento de datos:.*"
]
VERIFICATION_CATEGORIES = ["Verdad a medias", "Falso", "Engañoso", "Verdadero"]
RELEVANT_KEYWORDS = [
    'según', 'afirma', 'señala', 'datos', 'evidencia', 'verificación',
    'análisis', 'investigación', 'fuente', 'demostrado', 'resultado'
]
SPANISH_MONTHS = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
}
SOURCE_PATTERNS = [
    r'([\w\s]+) (dijo|afirmó|aseguró|declaró)',
    r'([\w\s]+), (dijo|afirmó|aseguró|declaró)',
    r'según ([\w\s]+)'
]
FALLBACK_URLS = [
    "https://www.newtral.es/espana-ayuda-militar-ucrania-factcheck/20250317/",
    "https://www.newtral.es/presion-fiscal-patxi-lopez-factcheck/20250312/",
    "https://www.newtral.es/mujeres-autonomas-madrid-factcheck/20250310/",
    "https://www.newtral.es/empresas-abandonan-cataluna-pepa-millan-factcheck/20250310/",
    "https://www.newtral.es/mannheim-nacionalidad-atropello-buxade-factcheck/20250306/"
]

# Selectores para extracción de elementos
SELECTORS = {
    'title': ["h1.post-title", "h1", ".article-title", "header h1", ".entry-title"],
    'verification': {
        ".card-text-marked-red": "Falso",
        ".card-text-marked-orange": "Engañoso",
        ".card-text-marked-pistachio": "Verdad a medias",
        ".card-text-marked-green": "Verdadero"
    },
    'date': [
        "time[datetime]", ".post-date", ".entry-date",
        "meta[property='article:published_time']", ".card-meta-date"
    ],
    'claim': [
        'blockquote', "span[style*='background-color']", "mark", "strong",
        "span.card-text-marked-pistachiomark", "div.claim p", "blockquote.claim",
        ".card-text-marked-orange", ".card-text-container .card-text-marked-orange mark",
        ".card-text-marked-red", ".card-text-marked-pistachio", ".card-text-marked-green",
        "p.single-main-contentfactchecks-methodology-result", 
        "div.article-content p:first-of-type", "p.destacado"
    ],
    'claim_source': ['.card-author-text-link', '.card-author-text span'],
    'content': [
        "div.entry-content", "div.article-content", "div.post-content",
        "article.post-content", "div.main-content", "div.content",
        "div.section-post-content"
    ],
    'author': [
        "div.author-name", "span.author-name", "meta[name='author']",
        ".post-author a", "a.author-link", "p.byline",
        "span.byline-author", ".article-author"
    ],
    'image': [
        "img.featured-image", "figure img", "div.main-image img",
        "img.post-thumbnail", "meta[property='og:image']",
        ".wp-post-image", ".card-img-bg"
    ],
    'fact_check_links': "//div[contains(@class, 'card-featured-archive') or contains(@class, 'card-featured-archive-small')]//a[contains(@class, 'card-title-link')]",
    'load_more_button': "vog-newtral-es-verification-list-load-more-btn"
}

class NewtralScraper(BaseScraper):
    """
    Specialized scraper for extracting fact-checks from Newtral.
    Uses Selenium for navigation and BeautifulSoup for parsing content.
    """
    def __init__(self, respect_robots=True):
        """
        Initialize the Newtral scraper with the base URL.
        
        Args:
            respect_robots (bool): Whether to respect robots.txt rules
        """
        super().__init__(
            base_url=BASE_URL,
            name="NewtralScraper",
            respect_robots=respect_robots
        )
        self.fact_check_url = FACT_CHECK_URL

    @contextmanager
    def _get_browser(self):
        """Context manager for browser session to ensure proper cleanup."""
        driver = None
        try:
            driver = self._initialize_webdriver()
            yield driver
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error closing WebDriver: {e}")

    def _initialize_webdriver(self):
        """Initialize and configure the Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # Add the current User-Agent to maintain consistency
        chrome_options.add_argument(f"user-agent={self.session.headers['User-Agent']}")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def _clean_text(self, text):
        """Clean text by removing unwanted content."""
        if not text:
            return ""
            
        # Remove cookie patterns and unwanted text
        for pattern in CLEANUP_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.DOTALL|re.IGNORECASE)
            
        # Remove extra spaces, line breaks and normalize
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _parse_date(self, date_str):
        """Parse date string into YYYY-MM-DD format."""
        try:
            # ISO format
            parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return parsed_date.strftime("%Y-%m-%d")
        except:
            # Spanish format (day/month/year)
            match = re.search(r'(\d{1,2})\s*[/.-]\s*(\d{1,2})\s*[/.-]\s*(\d{4})', date_str)
            if match:
                day, month, year = match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Spanish text format (day de month de year)
            match = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', date_str.lower())
            if match:
                day, month_name, year = match.groups()
                if month_name in SPANISH_MONTHS:
                    return f"{year}-{SPANISH_MONTHS[month_name]}-{day.zfill(2)}"
                    
        return None

    def _filter_paragraphs(self, paragraphs):
        """Filter and prioritize paragraphs by relevance."""
        cleaned_paragraphs = []
        priority_paragraphs = []
        
        for p in paragraphs:
            text = self._clean_text(p.get_text())
            
            # Filter paragraphs
            if (text and len(text) > 50 and 
                'cookies' not in text.lower() and 
                not text.startswith('Con tu consentimiento')):
                
                # Prioritize paragraphs with relevant keywords
                if any(keyword in text.lower() for keyword in RELEVANT_KEYWORDS):
                    priority_paragraphs.append(text)
                else:
                    cleaned_paragraphs.append(text)
                    
        # Combine priority + rest
        return priority_paragraphs + cleaned_paragraphs

    def _extract_element_with_selectors(self, soup, selectors, get_text=True):
        """Extract element using multiple selectors."""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True) if get_text else element
        return None

    def _extract_title(self, soup):
        """Extract article title."""
        return self._extract_element_with_selectors(soup, SELECTORS['title'])

    def _extract_claim(self, soup):
        """Extract the verified claim from article."""
        for selector in SELECTORS['claim']:
            claim_elements = soup.select(selector)
            
            for element in claim_elements:
                claim_text = element.get_text(strip=True)
                
                # Clean quotes and extra spaces
                claim_text = re.sub(r'^["""]|["""]$', '', claim_text)
                claim_text = re.sub(r'\s+', ' ', claim_text).strip()
                
                # Validate length and relevance
                if claim_text and 20 <= len(claim_text) <= 500:
                    return claim_text
                    
        return None

    def _extract_claim_source(self, soup):
        """Extract the source of the claim."""
        # Look in author card section
        author_element = soup.select_one(SELECTORS['claim_source'][0])
        if author_element:
            return author_element.get_text(strip=True)
            
        # Look in other places
        source_elements = soup.select(SELECTORS['claim_source'][1])
        if source_elements and len(source_elements) > 1:
            return source_elements[0].get_text(strip=True)
            
        # Try first paragraph
        first_paragraph = soup.select_one('.section-post-content p')
        if first_paragraph:
            text = first_paragraph.get_text(strip=True)
            for pattern in SOURCE_PATTERNS:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
                    
        return None

    def _extract_tags(self, soup):
        """Extract tags from article."""
        tags = []
        
        tag_section = soup.select_one('.section-post-tags')
        if tag_section:
            tag_elements = tag_section.select('.pill-outline')
            for tag_element in tag_elements:
                tag_text = tag_element.get_text(strip=True)
                if tag_text:
                    tags.append(tag_text)
                    
        return tags

    def _extract_author(self, soup):
        """Extract article author."""
        for selector in SELECTORS['author']:
            author_elements = soup.select(selector)
            
            for element in author_elements:
                author_text = element.get_text(strip=True)
                
                # Clean "Por " text and dates
                author_text = re.sub(r'^Por\s+', '', author_text, flags=re.IGNORECASE)
                author_text = re.sub(r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}', '', author_text)
                author_text = re.sub(r'\s+', ' ', author_text).strip()
                
                # Validate length
                if author_text and 2 <= len(author_text) <= 100:
                    return author_text
                    
        return None

    def _extract_content(self, soup):
        """Extract main article content."""
        # Try to extract with different selectors
        for selector in SELECTORS['content']:
            content_element = soup.select_one(selector)
            if content_element:
                paragraphs = content_element.find_all('p')
                cleaned_paragraphs = self._filter_paragraphs(paragraphs)
                content_text = ' '.join(cleaned_paragraphs)
                
                if len(content_text) > 100:
                    return content_text
                    
        # Fallback: extract from all paragraphs
        all_paragraphs = soup.find_all('p')
        fallback_paragraphs = self._filter_paragraphs(all_paragraphs)
        fallback_content = ' '.join(fallback_paragraphs)
        
        return fallback_content if len(fallback_content) > 100 else None

    def _extract_verification_category(self, soup):
        """Extract verification category (True, False, etc)."""
        # Try class-based approach
        for selector, category in SELECTORS['verification'].items():
            element = soup.select_one(selector)
            if element:
                return category
        
        # Try text-based approach
        for category in VERIFICATION_CATEGORIES:
            # Direct text
            elements = soup.find_all(string=lambda text: category in text)
            
            # Elements with specific style/class
            if not elements:
                elements = soup.select(f"*:contains('{category}')")
                
            if elements:
                return category
                
        return None

    def _extract_date(self, soup, url=None):
        """Extract publish date from article."""
        # First try URL
        if url:
            url_match = re.search(r'/(\d{8})/', url)
            if url_match:
                date_str = url_match.group(1)
                return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                
        # Try page elements
        for selector in SELECTORS['date']:
            date_element = soup.select_one(selector)
            if date_element:
                if selector == "meta[property='article:published_time']":
                    date_str = date_element.get('content', '')
                else:
                    date_str = date_element.get_text(strip=True)
                    
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    return parsed_date
                    
        return None

    def _extract_image(self, soup):
        """Extract featured image from article."""
        for selector in SELECTORS['image']:
            image_element = soup.select_one(selector)
            if image_element:
                if selector == "meta[property='og:image']":
                    image_url = image_element.get('content')
                else:
                    image_url = (image_element.get('src') or
                                image_element.get('data-src') or
                                image_element.get('data-original'))
                                
                if image_url:
                    # Convert relative URLs
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url
                    elif image_url.startswith('/'):
                        image_url = f"{self.base_url.rstrip('/')}{image_url}"
                        
                    if image_url.startswith('http'):
                        return image_url
                        
        return None

    def _get_fact_check_urls(self, limit):
        """Extract URLs from fact-check section with pagination."""
        with self._get_browser() as driver:
            try:
                driver.get(self.fact_check_url)
                time.sleep(3)
                
                urls = []
                pagination_attempts = 0
                
                # Function to extract URLs from current page
                def extract_current_urls():
                    links = driver.find_elements(By.XPATH, SELECTORS['fact_check_links'])
                    new_count = 0
                    
                    for link in links:
                        url = link.get_attribute('href')
                        if url and url not in urls:
                            urls.append(url)
                            new_count += 1
                            logger.info(f"Found URL: {url}")
                    
                    return new_count
                
                # Extract initial URLs
                extract_current_urls()
                
                # Keep loading more until limit reached or max attempts
                while len(urls) < limit and pagination_attempts < 20:
                    try:
                        # Find and scroll to load more button
                        load_more = driver.find_element(By.ID, SELECTORS['load_more_button'])
                        
                        if not load_more.is_displayed():
                            logger.info("Load more button not visible")
                            break
                        
                        # Scroll to button and click
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", load_more)
                        
                        # Wait for new content to load
                        time.sleep(LOAD_MORE_WAIT)
                        
                        # Extract new URLs
                        new_count = extract_current_urls()
                        
                        # Stop if no new URLs found
                        if new_count == 0:
                            logger.info("No new URLs found after clicking 'Load more'")
                            break
                        
                        pagination_attempts += 1
                        logger.info(f"Loaded page {pagination_attempts}, total URLs: {len(urls)}")
                        
                    except Exception as e:
                        logger.warning(f"Error clicking 'Load more' button: {e}")
                        break
                
                if not urls:
                    logger.warning("No URLs found, using predefined URLs")
                    return FALLBACK_URLS[:limit]
                
                return urls[:limit]
                
            except Exception as e:
                logger.error(f"Error extracting URLs: {e}")
                return FALLBACK_URLS[:limit]

    def _scrape_fact_check_article(self, url):
        """Extract data from individual fact-check article."""
        logger.info(f"Extracting fact-check article: {url}")
        
        with self._get_browser() as driver:
            try:
                # Navigate to URL and wait for content
                driver.get(url)
                WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1, .post-title, .article-content"))
                )
                
                # Parse HTML
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Extract all article data
                title = self._extract_title(soup)
                category = self._extract_verification_category(soup)
                publish_date = self._extract_date(soup, url)
                content = self._extract_content(soup)
                claim = self._extract_claim(soup)
                claim_source = self._extract_claim_source(soup)
                image_url = self._extract_image(soup)
                tags = self._extract_tags(soup)
                author = self._extract_author(soup)
                
                # Build result dictionary
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
                
                logger.info(f"Data extracted: {article['title']}")
                return article
                
            except Exception as e:
                logger.error(f"Error extracting article {url}: {e}")
                return None

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
        logger.info(f"Starting extraction with limit: {limit}")
        
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