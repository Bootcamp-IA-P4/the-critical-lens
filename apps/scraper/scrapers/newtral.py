import logging
import time
import re
from contextlib import contextmanager
from django.utils import timezone
from .base import BaseScraper

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class NewtralScraper(BaseScraper):
    """
    Scraper to extract fact-checks from the Newtral website.
    """
    def __init__(self, respect_robots=True, **kwargs):
        super().__init__(
            base_url="https://www.newtral.es",
            name="NewtralScraper",
            respect_robots=respect_robots,
            **kwargs
        )
        self.fact_check_url = "https://www.newtral.es/zona-verificacion/fact-check/"

    @contextmanager
    def _get_browser(self):
        """Sets up and returns a Chrome browser for scraping."""
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--no-sandbox")
            
            # Use the same user agent as the base scraper
            chrome_options.add_argument(f"user-agent={self.session.headers['User-Agent']}")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            yield driver
        finally:
            if driver:
                driver.quit()

    def _get_fact_check_urls(self, limit):
        """Gets fact-check URLs from the main page."""
        # Use the base class to check robots.txt
        if self.respect_robots and not self._can_access(self.fact_check_url):
            return []
            
        with self._get_browser() as driver:
            try:
                driver.get(self.fact_check_url)
                time.sleep(3)
                
                urls = []
                click_attempts = 0
                
                # Extract current URLs
                links = driver.find_elements(By.CSS_SELECTOR, ".card-title-link")
                for link in links:
                    url = link.get_attribute('href')
                    if url and url not in urls:
                        urls.append(url)
                
                # Click on "Load more" until reaching the limit
                while len(urls) < limit and click_attempts < 30:
                    try:
                        load_more = driver.find_element(By.ID, "vog-newtral-es-verification-list-load-more-btn")
                        
                        if not load_more.is_displayed():
                            break
                        
                        driver.execute_script("arguments[0].scrollIntoView();", load_more)
                        driver.execute_script("arguments[0].click();", load_more)
                        
                        time.sleep(3)
                        
                        links = driver.find_elements(By.CSS_SELECTOR, ".card-title-link")
                        for link in links:
                            url = link.get_attribute('href')
                            if url and url not in urls:
                                urls.append(url)
                        
                        click_attempts += 1
                        
                    except Exception as e:
                        logger.warning(f"Error al hacer clic en 'Cargar más': {e}")
                        break
                
                # Filter URLs based on robots.txt
                if self.respect_robots:
                    urls = [url for url in urls if self._can_access(url)]
                
                return urls[:limit]
                
            except Exception as e:
                logger.error(f"Error al extraer URLs: {e}")
                return []

    def _extract_article_data(self, url):
        """Extracts data from an individual fact-check article."""
        with self._get_browser() as driver:
            try:
                driver.get(url)
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".post-title-1, h1"))
                )
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Extract basic article data
                title_element = soup.select_one(".post-title-1") or soup.select_one("h1")
                title = title_element.get_text(strip=True) if title_element else None
                
                date_element = soup.select_one(".post-date")
                from apps.scraper.models import FactCheckArticle
                publish_date = FactCheckArticle.parse_date(date_element.get_text(strip=True)) if date_element else None
                
                author_element = soup.select_one(".post-author .author-link")
                author = author_element.get_text(strip=True) if author_element else None
                
                # Extract content
                content_element = soup.select_one(".section-post-content")
                content = ""
                if content_element:
                    paragraphs = content_element.find_all('p')
                    content = " ".join([p.get_text(strip=True) for p in paragraphs])
                
                # Extract claim
                mark_element = soup.select_one("mark")
                claim = None
                if mark_element:
                    claim = mark_element.get_text(strip=True)
                    claim = re.sub(r'^["""]|["""]$', '', claim)
                
                # Extract claim source
                claim_source_element = soup.select_one(".card-author-text-link")
                claim_source = claim_source_element.get_text(strip=True) if claim_source_element else None
                
                # Find verification category
                verification_category = None
                verification_selectors = {
                    ".card-text-marked-red": "Falso",
                    ".card-text-marked-orange": "Engañoso",
                    ".card-text-marked-pistachio": "Verdad a medias",
                    ".card-text-marked-green": "Verdadero"
                }
                
                for selector, category in verification_selectors.items():
                    if soup.select_one(selector):
                        verification_category = category
                        break
                
                # Fallback method for category
                if not verification_category:
                    possible_categories = ["Verdad a medias", "Falso", "Engañoso", "Verdadero"]
                    for category in possible_categories:
                        elements = soup.find_all(string=lambda text: category in text if text else False)
                        if elements:
                            verification_category = category
                            break
                
                # Extract tags
                tags = []
                tag_elements = soup.select(".section-post-tags .pill-outline")
                for tag_element in tag_elements:
                    tag_text = tag_element.get_text(strip=True)
                    if tag_text:
                        tags.append(tag_text)
                
                # Return article data
                return {
                    "title": title,
                    "url": url,
                    "verification_category": verification_category,
                    "publish_date": publish_date,
                    "claim": claim,
                    "claim_source": claim_source,
                    "content": content,
                    "tags": tags,
                    "author": author,
                    "scraped_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
            except Exception as e:
                logger.error(f"Error al extraer artículo {url}: {e}")
                return None

    def _can_access(self, url):
        """Check if we can access a URL based on robots.txt"""
        if not self.respect_robots:
            return True
        return self.robots_parser.can_fetch(url, self.session.headers.get('User-Agent'))

    def scrape(self, limit=10, **kwargs):
        """
        Main method to extract fact-checks from Newtral.
        """
        logger.info(f"Iniciando extracción con límite: {limit}")
        
        # Rotate user agent
        self.rotate_user_agent()
        
        # Get article URLs
        article_urls = self._get_fact_check_urls(limit)
        logger.info(f"URLs a procesar: {len(article_urls)}")
        
        # Extract articles
        articles = []
        for url in article_urls:
            article = self._extract_article_data(url)
            if article:
                articles.append(article)
                logger.info(f"Artículo extraído: {article.get('title', 'Sin título')}")
        
        logger.info(f"Extracción completada. {len(articles)} artículos extraídos")
        return articles