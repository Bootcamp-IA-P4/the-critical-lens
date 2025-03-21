import logging
import time
from datetime import datetime
import re
from contextlib import contextmanager
from django.utils import timezone
from apps.scraper.utils.logging_config import configure_logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

logger = configure_logging()

class NewtralScraper:
    """
    Scraper para extraer fact-checks del sitio web de Newtral.
    """
    def __init__(self, respect_robots=True, **kwargs):
        self.base_url = "https://www.newtral.es"
        self.fact_check_url = "https://www.newtral.es/zona-verificacion/fact-check/"
        self.respect_robots = respect_robots

    @contextmanager
    def _get_browser(self):
        """Configura y devuelve un navegador Chrome para el scraping."""
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--no-sandbox")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            yield driver
        finally:
            if driver:
                driver.quit()

    def _clean_text(self, text):
        """Limpia el texto removiendo espacios extra y saltos de línea."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    def _get_fact_check_urls(self, limit):
        """Obtiene URLs de fact-checks desde la página principal."""
        with self._get_browser() as driver:
            try:
                driver.get(self.fact_check_url)
                time.sleep(3)
                
                urls = []
                click_attempts = 0
                
                # Extraer URLs actuales
                links = driver.find_elements(By.CSS_SELECTOR, ".card-title-link")
                for link in links:
                    url = link.get_attribute('href')
                    if url and url not in urls:
                        urls.append(url)
                
                # Hacer clic en "Cargar más" hasta alcanzar el límite
                while len(urls) < limit and click_attempts < 30:
                    try:
                        # Buscar botón de "Cargar más"
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
                
                return urls[:limit]
                
            except Exception as e:
                logger.error(f"Error al extraer URLs: {e}")
                return []

    def _extract_article_data(self, url):
        """Extrae datos de un artículo de fact-check individual."""
        with self._get_browser() as driver:
            try:
                driver.get(url)
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".post-title-1, h1"))
                )
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Título
                title_element = soup.select_one(".post-title-1") or soup.select_one("h1")
                title = title_element.get_text(strip=True) if title_element else None
                
                # Fecha
                date_element = soup.select_one(".post-date")
                if date_element:
                    date_str = date_element.get_text(strip=True)
                    from apps.scraper.models import FactCheckArticle
                    publish_date = FactCheckArticle.parse_date(date_str)
                else:
                    publish_date = None
                
                # Autor
                author_element = soup.select_one(".post-author .author-link")
                author = author_element.get_text(strip=True) if author_element else None
                
                # Contenido
                content_element = soup.select_one(".section-post-content")
                content = ""
                if content_element:
                    paragraphs = content_element.find_all('p')
                    content = " ".join([p.get_text(strip=True) for p in paragraphs])
                    content = self._clean_text(content)
                
                # Claim (afirmación verificada)
                mark_element = soup.select_one("mark")
                claim = None
                if mark_element:
                    claim = mark_element.get_text(strip=True)
                    claim = re.sub(r'^["""]|["""]$', '', claim)
                    claim = self._clean_text(claim)
                
                # Autor del claim
                claim_source_element = soup.select_one(".card-author-text-link")
                claim_source = claim_source_element.get_text(strip=True) if claim_source_element else None
                
                # Categoría de verificación
                verification_category = None
                
                # Primer intento: Enfoque basado en clases CSS
                verification_selectors = {
                    ".card-text-marked-red": "Falso",
                    ".card-text-marked-orange": "Engañoso",
                    ".card-text-marked-pistachio": "Verdad a medias",
                    ".card-text-marked-green": "Verdadero"
                }
                
                for selector, category in verification_selectors.items():
                    element = soup.select_one(selector)
                    if element:
                        verification_category = category
                        break
                
                # Segundo intento: Enfoque basado en texto
                if not verification_category:
                    possible_categories = ["Verdad a medias", "Falso", "Engañoso", "Verdadero"]
                    
                    for category in possible_categories:
                        # Buscar el texto directo en cualquier elemento
                        elements = soup.find_all(string=lambda text: category in text if text else False)
                        
                        # Buscar elementos con estilo o clase específica que contengan el texto
                        if not elements:
                            try:
                                elements = soup.select(f"*:contains('{category}')")
                            except:
                                continue
                                
                        if elements:
                            verification_category = category
                            break
                
                # Etiquetas
                tags = []
                tag_elements = soup.select(".section-post-tags .pill-outline")
                for tag_element in tag_elements:
                    tag_text = tag_element.get_text(strip=True)
                    if tag_text:
                        tags.append(tag_text)
                
                # Crear diccionario con los datos extraídos
                article = {
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
                
                return article
                
            except Exception as e:
                logger.error(f"Error al extraer artículo {url}: {e}")
                return None

    def scrape(self, limit=10, **kwargs):
        """
        Método principal para extraer fact-checks de Newtral.
        
        Args:
            limit (int): Número máximo de artículos a extraer
            
        Returns:
            list: Lista de artículos extraídos
        """
        logger.info(f"Iniciando extracción con límite: {limit}")
        
        article_urls = self._get_fact_check_urls(limit)
        logger.info(f"URLs a procesar: {len(article_urls)}")
        
        articles = []
        for url in article_urls:
            article = self._extract_article_data(url)
            if article:
                articles.append(article)
                logger.info(f"Artículo extraído: {article.get('title', 'Sin título')}")
        
        logger.info(f"Extracción completada. {len(articles)} artículos extraídos")
        return articles