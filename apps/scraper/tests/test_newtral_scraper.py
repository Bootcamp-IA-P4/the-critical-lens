import sys
import os
import json
import logging
from datetime import datetime

# Configure project path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.insert(0, project_root)

# Specific imports
from apps.scraper.scrapers import NewtralScraper
from apps.scraper.utils.logging_config import configure_logging

# Configure logging
logger = configure_logging(log_level=logging.INFO)

def validate_article(article):
    """
    Validate the structure and content of an extracted article.
    
    Args:
        article (dict): Article to validate
    
    Returns:
        bool: True if the article is valid, False otherwise
    """
    # Required fields
    required_fields = [
        'title', 'url', 'verification_category', 
        'publish_date', 'scraped_at'
    ]
    
    # Validations
    for field in required_fields:
        if not article.get(field):
            logger.error(f"Invalid article: missing '{field}' field")
            return False
    
    # Additional validations
    try:
        # Validate URL
        if not article['url'].startswith('https://www.newtral.es/'):
            logger.error(f"Invalid URL: {article['url']}")
            return False
        
        # Validate verification category
        valid_categories = ["Verdad a medias", "Falso", "Engañoso", "Verdadero"]
        if article['verification_category'] not in valid_categories:
            logger.error(f"Invalid category: {article['verification_category']}")
            return False
        
        # Validate date
        datetime.strptime(article['publish_date'], "%Y-%m-%d")
        datetime.strptime(article['scraped_at'], "%Y-%m-%d %H:%M:%S")
        
        # Validate title
        if len(article['title']) < 10 or len(article['title']) > 250:
            logger.error(f"Invalid title: {article['title']}")
            return False
        
    except (ValueError, TypeError) as e:
        logger.error(f"Validation error: {e}")
        return False
    
    return True

def test_newtral_scraper():
    """
    Test the Newtral scraper with various scenarios.
    """
    print("Testing Newtral Scraper...")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(project_root, 'scraper_output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize scraper
    scraper = NewtralScraper()
    
    try:
        # Scenario 1: Extraction with default limit
        logger.info("Testing extraction with default limit")
        default_articles = scraper.scrape()
        
        # Scenario 2: Extraction with custom limit
        logger.info("Testing extraction with a limit of 3 articles")
        limited_articles = scraper.scrape(limit=3)
        
        # Validate results
        print("\nValidating results...")
        
        # Validate default extraction
        if not default_articles:
            logger.error("No articles were extracted with default limit")
            return
        
        # Validate extraction with custom limit
        if not limited_articles or len(limited_articles) > 3:
            logger.error("Error in extraction with custom limit")
            return
        
        # Validate each article
        print("\nValidating articles...")
        valid_default_articles = [a for a in default_articles if validate_article(a)]
        valid_limited_articles = [a for a in limited_articles if validate_article(a)]
        
        # Save results to JSON file
        output_file = os.path.join(output_dir, 'newtral_results.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(limited_articles, f, ensure_ascii=False, indent=2)
        
        # Print summary
        print("\nExtraction Summary:")
        print(f"Articles extracted (default limit): {len(default_articles)}")
        print(f"Valid articles (default limit): {len(valid_default_articles)}")
        print(f"Articles extracted (limit 3): {len(limited_articles)}")
        print(f"Valid articles (limit 3): {len(valid_limited_articles)}")
        
        # Details of valid articles
        for i, article in enumerate(limited_articles, 1):
            print(f"\nArticle {i}: {article['title']}")
            print(f"    Category: {article['verification_category']}")
            if article.get('claim'):
                print(f"    Claim: {article['claim'][:100]}...")
        
        # Final verification
        assert len(valid_limited_articles) > 0, "No valid articles found"
        print("\nTest completed successfully")
    
    except Exception as e:
        logger.error(f"Error in scraper test: {e}")
        raise

if __name__ == "__main__":
    test_newtral_scraper()
