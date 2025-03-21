import logging
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from .models import FactCheckArticle, VerificationCategory
from .scrapers.newtral import NewtralScraper
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

class ScraperService:
    """
    Servicio para coordinar la extracción de datos y su persistencia en la base de datos.
    
    Esta clase gestiona la extracción de datos usando scrapers especializados
    y almacena los resultados en la base de datos de manera transaccional.
    """
    
    def scrape_newtral(self, limit=10, respect_robots=True):
        """
        Extrae fact-checks de Newtral y los almacena en la base de datos.
        
        Args:
            limit (int): Número máximo de artículos a extraer.
            respect_robots (bool): Si se deben respetar las directivas de robots.txt.
            
        Returns:
            tuple: (total_articles, new_articles, updated_articles, failed_articles)
        """
        from apps.scraper.utils.logging_config import configure_logging
        logger = configure_logging()

        logger.info(f"Iniciando extracción de fact-checks de Newtral (limit={limit})")
        
        # Inicializar scraper de Newtral
        scraper = NewtralScraper(respect_robots=respect_robots)
        
        # Extraer artículos
        extracted_articles = []
        try:
            extracted_articles = scraper.scrape(limit=limit)
            logger.info(f"Extracción completada: {len(extracted_articles)} artículos obtenidos")
        except Exception as e:
            logger.error(f"Error durante la extracción: {e}")
            return 0, 0, 0, 0
        
        # Estadísticas para devolver
        total_articles = len(extracted_articles)
        new_articles = 0
        updated_articles = 0
        failed_articles = 0
        
        # Procesar y guardar cada artículo
        for article_data in extracted_articles:
            try:
                with transaction.atomic():
                    # Extraer datos
                    url = article_data.get('url')
                    title = article_data.get('title')
                    publish_date = article_data.get('publish_date')
                    
                    if not url or not title:
                        logger.warning(f"Artículo descartado por falta de datos esenciales: {article_data}")
                        failed_articles += 1
                        continue
                    
                    # Parsear fecha usando el método del modelo
                    parsed_date = FactCheckArticle.parse_date(publish_date)
                    
                    # Encontrar o crear categoría de verificación
                    verification_category = None
                    category_name = article_data.get('verification_category')
                    if category_name:
                        verification_category, _ = VerificationCategory.objects.get_or_create(
                            name=category_name,
                            defaults={'description': f'Categoría de verificación: {category_name}'}
                        )
                    
                    # Comprobar si el artículo ya existe (por URL)
                    article, created = FactCheckArticle.objects.get_or_create(
                        url=url,
                        defaults={
                            'title': title,
                            'publish_date': parsed_date,
                            'claim': article_data.get('claim', ''),
                            'claim_source': article_data.get('claim_source', ''),
                            'content': article_data.get('content', ''),
                            'tags': article_data.get('tags', []),
                            'author': article_data.get('author', ''),
                            'verification_category': verification_category,
                            'scraped_at': timezone.now(),
                            'is_processed': False
                        }
                    )
                    
                    if created:
                        new_articles += 1
                        logger.info(f"Nuevo artículo creado: {title}")
                    else:
                        # Actualizar artículo existente
                        article.title = title
                        if parsed_date:
                            article.publish_date = parsed_date
                        article.claim = article_data.get('claim', article.claim)
                        article.claim_source = article_data.get('claim_source', article.claim_source)
                        article.content = article_data.get('content', article.content)
                        article.tags = article_data.get('tags', article.tags)
                        article.author = article_data.get('author', article.author)
                        article.verification_category = verification_category or article.verification_category
                        article.scraped_at = timezone.now()
                        article.save()
                        
                        updated_articles += 1
                        logger.info(f"Artículo actualizado: {title}")
            
            except Exception as e:
                failed_articles += 1
                logger.error(f"Error procesando artículo: {e}")
        
        return total_articles, new_articles, updated_articles, failed_articles