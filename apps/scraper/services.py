import logging
from datetime import datetime
from django.db import transaction
from .models import FactCheckArticle, VerificationCategory
from .scrapers.newtral import NewtralScraper

logger = logging.getLogger(__name__)

class ScraperService:
    """
    Service to coordinate data extraction and persistence in the database.
    
    This class manages data extraction using specialized scrapers
    and stores the results in the database in a transactional manner.
    """
    
    def scrape_newtral(self, limit=10, respect_robots=True):
        """
        Extracts fact-checks from Newtral and stores them in the database.
        
        Args:
            limit (int): Maximum number of articles to extract.
            respect_robots (bool): Whether to respect robots.txt directives.
            
        Returns:
            tuple: (total_articles, new_articles, updated_articles, failed_articles)
        """
        logger.info(f"Starting extraction of Newtral fact-checks (limit={limit})")
        
        # Initialize Newtral scraper
        scraper = NewtralScraper(respect_robots=respect_robots)
        
        # Extract articles
        extracted_articles = []
        try:
            extracted_articles = scraper.scrape(limit=limit)
            logger.info(f"Extraction completed: {len(extracted_articles)} articles obtained")
        except Exception as e:
            logger.error(f"Error during extraction: {e}")
            return 0, 0, 0, 0
        
        # Statistics for return
        total_articles = len(extracted_articles)
        new_articles = 0
        updated_articles = 0
        failed_articles = 0
        
        # Process and save each article
        for article_data in extracted_articles:
            try:
                with transaction.atomic():
                    # Extract data
                    url = article_data.get('url')
                    title = article_data.get('title')
                    publish_date = article_data.get('publish_date')
                    
                    if not url or not title:
                        logger.warning(f"Article discarded due to lack of essential data: {article_data}")
                        failed_articles += 1
                        continue
                    
                    # Find or create verification category
                    verification_category = None
                    category_name = article_data.get('verification_category')
                    if category_name:
                        verification_category, _ = VerificationCategory.objects.get_or_create(
                            name=category_name,
                            defaults={'description': f'Verification category: {category_name}'}
                        )
                    
                    # Check if the article already exists (by URL)
                    article, created = FactCheckArticle.objects.get_or_create(
                        url=url,
                        defaults={
                            'title': title,
                            'publish_date': publish_date if publish_date else None,
                            'claim': article_data.get('claim', ''),
                            'claim_source': article_data.get('claim_source', ''),
                            'content': article_data.get('content', ''),
                            'image_url': article_data.get('image_url', ''),
                            'tags': article_data.get('tags', []),
                            'author': article_data.get('author', ''),
                            'verification_category': verification_category,
                            'scraped_at': datetime.now(),
                            'is_processed': False
                        }
                    )
                    
                    if created:
                        new_articles += 1
                        logger.info(f"New article created: {title}")
                    else:
                        # Update existing article
                        article.title = title
                        article.publish_date = publish_date if publish_date else article.publish_date
                        article.claim = article_data.get('claim', article.claim)
                        article.claim_source = article_data.get('claim_source', article.claim_source)
                        article.content = article_data.get('content', article.content)
                        article.image_url = article_data.get('image_url', article.image_url)
                        article.tags = article_data.get('tags', article.tags)
                        article.author = article_data.get('author', article.author)
                        article.verification_category = verification_category or article.verification_category
                        article.scraped_at = datetime.now()
                        article.save()
                        
                        updated_articles += 1
                        logger.info(f"Article updated: {title}")
            
            except Exception as e:
                failed_articles += 1
                logger.error(f"Error processing article: {e}")
        
        return total_articles, new_articles, updated_articles, failed_articles