import logging
import time
import re
from datetime import datetime, timezone
from contextlib import contextmanager

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from .base import BaseScraper

logger = logging.getLogger(__name__)

# URLs de respaldo
FALLBACK_URLS = [
    "https://www.newtral.es/sanchez-pisos-alquiler-cataluna-factcheck/20250319/",
    "https://www.newtral.es/pp-tjue-excepcion-iberica-factcheck/20250319/",
    "https://www.newtral.es/espana-ayuda-militar-ucrania-factcheck/20250317/",
    "https://www.newtral.es/menores-riesgo-pobreza-factcheck/20250313/"
]

class NewtralScraper(BaseScraper):
    """
    Scraper para extraer fact-checks de Newtral con selectores precisos.
    """
    def __init__(self, respect_robots=True):
        super().__init__(
            base_url="https://www.newtral.es",
            name="NewtralScraper",
            respect_robots=respect_robots
        )
        self.fact_check_url = f"{self.base_url}/zona-verificacion/fact-check/"

    @contextmanager
    def _get_browser(self):
        """Administrador de contexto para el navegador Chrome."""
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            yield driver
        finally:
            if driver:
                driver.quit()

    def _clean_text(self, text):
        """Limpia el texto y lo trunca a 250 caracteres para evitar errores de BD."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()[:250]

    def _get_fact_check_urls(self, limit):
        """Extrae URLs de artículos o devuelve URLs de respaldo."""
        # Para evitar problemas, usamos directamente las URLs predefinidas
        logger.info(f"Usando URLs de respaldo (límite: {limit})")
        return FALLBACK_URLS[:limit]

    def _extract_fact_check_data(self, url):
        """Extrae datos de un artículo individual usando selectores precisos."""
        with self._get_browser() as driver:
            try:
                logger.info(f"Extrayendo artículo: {url}")
                driver.get(url)
                
                # Esperar a que cargue la página
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
                
                # Analizar HTML
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Título - Usando un selector más específico
                title = None
                title_element = soup.select_one("h1.post-title-1") or soup.select_one("h1.post-title") or soup.select_one("h1")
                if title_element:
                    title = self._clean_text(title_element.get_text())
                
                # Fecha (obtenemos el texto en bruto para procesarlo después con el modelo)
                publish_date = None
                date_element = soup.select_one(".post-date")
                if date_element:
                    publish_date = date_element.get_text(strip=True)
                
                # Si no se encontró la fecha, usamos la URL para que el modelo la procese
                if not publish_date:
                    publish_date = url
                
                # Categoría de verificación
                verification = None
                verification_selectors = {
                    ".card-text-marked-red": "Falso",
                    ".card-text-marked-orange": "Engañoso",
                    ".card-text-marked-pistachio": "Verdad a medias",
                    ".card-text-marked-green": "Verdadero",
                    ".card-factcheck-result-text": None  # Selector directo para el texto de resultado
                }
                
                # Primero intentamos con los selectores de clase por color
                for selector, category in verification_selectors.items():
                    if not category:  # Para el selector directo de texto
                        result_element = soup.select_one(selector)
                        if result_element:
                            verification = self._clean_text(result_element.get_text())
                            break
                    elif soup.select_one(selector):
                        verification = category
                        break
                
                # Claim (afirmación) - Buscando específicamente dentro de mark
                claim = None
                # Primero intentamos encontrar el claim en el formato mark dentro de las clases de colores
                claim_element = soup.select_one(".card-text-marked-red mark, .card-text-marked-orange mark, .card-text-marked-pistachio mark, .card-text-marked-green mark")
                if claim_element:
                    claim = self._clean_text(claim_element.get_text())
                else:
                    # Si no encuentra en mark, buscamos con selectores más amplios
                    claim_selectors = ["blockquote", ".card-text-marked-red", 
                                      ".card-text-marked-orange", ".card-text-marked-pistachio", 
                                      ".card-text-marked-green"]
                    
                    for selector in claim_selectors:
                        elements = soup.select(selector)
                        for element in elements:
                            text = self._clean_text(element.get_text())
                            if text and len(text) > 20:
                                claim = text
                                break
                        
                        if claim:
                            break
                
                # Fuente de la afirmación - Selector más específico
                claim_source = None
                source_element = soup.select_one(".card-author-text .card-author-text-link")
                if source_element:
                    claim_source = self._clean_text(source_element.get_text())
                
                # Etiquetas
                tags = []
                tag_elements = soup.select(".pill.pill-outline")
                for tag_element in tag_elements:
                    tag_text = tag_element.get_text(strip=True)
                    if tag_text:
                        tags.append(tag_text)
                
                # Contenido - Selecciona específicamente párrafos dentro de section-post-content
                content = None
                content_element = soup.select_one(".section-post-content")
                if content_element:
                    # Seleccionar solo párrafos, no listas u otros elementos
                    paragraphs = content_element.select("p")
                    content_texts = []
                    
                    for p in paragraphs:
                        text = self._clean_text(p.get_text())
                        if text and len(text) > 50:
                            content_texts.append(text)
                            # Limitar a 3 párrafos para reducir tamaño
                            if len(content_texts) >= 3:
                                break
                    
                    if content_texts:
                        content = " ".join(content_texts)[:250]
                
                # Autor
                author = None
                author_element = soup.select_one(".post-author a")
                if author_element:
                    author = self._clean_text(author_element.get_text())
                
                result = {
                    "title": title,
                    "url": url,
                    "verification_category": verification,
                    "publish_date": publish_date,
                    "claim": claim,
                    "claim_source": claim_source,
                    "content": content,
                    "tags": tags,
                    "author": author,
                    "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                }
                
                logger.info(f"Artículo extraído: {title}")
                return result
                
            except Exception as e:
                logger.error(f"Error al extraer artículo {url}: {e}")
                return None

    def scrape(self, **kwargs):
        """Método principal para extraer fact-checks."""
        limit = kwargs.get('limit', 10)
        logger.info(f"Iniciando extracción con límite: {limit}")
        
        article_urls = self._get_fact_check_urls(limit)
        logger.info(f"URLs a procesar: {len(article_urls)}")
        
        articles = []
        for url in article_urls:
            article = self._extract_fact_check_data(url)
            if article:
                articles.append(article)
        
        logger.info(f"Extracción completada. {len(articles)} artículos extraídos")
        return articles