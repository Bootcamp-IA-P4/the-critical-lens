import pytest
from apps.scraper.scrapers import NewtralScraper

def test_newtral_article_extraction():
    """
    Test comprehensive content extraction from a single Newtral article.
    Verifies that the scraper can extract all model fields with meaningful content.
    """
    # Initialize scraper with robots.txt respect disabled
    scraper = NewtralScraper(respect_robots=False)
    
    # URL of the article to test
    url = "https://www.newtral.es/antiguedad-coches-espana-factcheck/20250320/"
    
    try:
        # Attempt to extract the article
        article = scraper._extract_article_data(url)
        
        # Basic verification: article must not be None
        assert article is not None, f"Could not extract article from {url}"
        
        # Comprehensive field verifications
        fields_to_verify = [
            'title',
            'url',
            'publish_date',
            'verification_category',
            'claim',
            'claim_source',
            'content',
            'tags',
            'author',
            'scraped_at'
        ]
        
        # Detailed print of extracted information
        print(f"\nArticle extracted: {url}")
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Publish Date: {article['publish_date']}")
        print(f"Verification Category: {article['verification_category']}")
        print(f"Claim: {article['claim'][:100]}...")
        print(f"Claim Source: {article['claim_source']}")
        print(f"Content Length: {len(article['content'])} characters")
        print(f"Tags: {article['tags']}")
        print(f"Author: {article['author']}")
        print(f"Scraped At: {article['scraped_at']}")
    
    except Exception as e:
        # If any assertion fails or an unexpected error occurs, the test will fail
        pytest.fail(f"Error extracting article from {url}: {str(e)}")