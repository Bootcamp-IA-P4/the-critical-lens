from django.shortcuts import render
from django.db.models import Count
import ast
import json
from apps.scraper.models import FactCheckArticle

def get_verification_stats(total_articles):
    """
    Get statistics about verification categories.
    
    Args:
        total_articles: Total number of articles for percentage calculation
        
    Returns:
        List of dictionaries with category stats
    """
    distribution = list(FactCheckArticle.objects.values(
        'verification_category__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count'))
    
    # Calculate percentages 
    for item in distribution:
        item['percentage'] = round((item['count'] / total_articles) * 100, 1)
    
    return distribution

def get_source_stats(total_articles):
    """
    Get statistics about claim sources.
    
    Args:
        total_articles: Total number of articles for percentage calculation
        
    Returns:
        List of dictionaries with source stats (limited to top 10)
    """
    # Get top 10 sources
    distribution = list(FactCheckArticle.objects.values(
        'claim_source'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10])
    
    # Calculate percentages 
    for item in distribution:
        item['percentage'] = round((item['count'] / total_articles) * 100, 1)
    
    return distribution

def get_tag_stats(total_articles):
    """
    Get statistics about article tags.
    
    Args:
        total_articles: Total number of articles for percentage calculation
        
    Returns:
        List of dictionaries with tag stats (limited to top 15)
    """
    tags_count = {}
    articles_with_tags = FactCheckArticle.objects.exclude(tags='').values_list('tags', flat=True)
    
    for article_tags in articles_with_tags:
        # Convert string representation of list to actual list
        tag_list = ast.literal_eval(article_tags)
        
        # Count each tag 
        for tag in tag_list:
            tags_count[tag] = tags_count.get(tag, 0) + 1
    
    # Convert to sorted list and calculate percentages
    distribution = [
        {'tag': tag, 'count': count, 'percentage': round((count / total_articles) * 100, 1)}
        for tag, count in tags_count.items()
    ]
    distribution.sort(key=lambda x: x['count'], reverse=True)
    return distribution[:15]  # Top 15 tags

def statistics(request):
    """
    View for displaying statistics about fact-checked articles.
    Renders the statistics template with data for visualization.
    """
    # We assume there are always articles available
    total_articles = FactCheckArticle.objects.count()
    
    # Get statistics
    verification_distribution = get_verification_stats(total_articles)
    source_distribution = get_source_stats(total_articles)
    tags_distribution = get_tag_stats(total_articles)
    
    # Prepare data for charts
    chart_data = {
        'verification': {
            'labels': [item['verification_category__name'] for item in verification_distribution],
            'counts': [item['count'] for item in verification_distribution],
            'percentages': [item['percentage'] for item in verification_distribution],
            'colors': ['#ff6b6b', '#feca57', '#54a0ff', '#1dd1a1']  
        },
        'source': {
            'labels': [item['claim_source'] for item in source_distribution],
            'counts': [item['count'] for item in source_distribution],
            'percentages': [item['percentage'] for item in source_distribution]
        },
        'tags': {
            'labels': [item['tag'] for item in tags_distribution],
            'counts': [item['count'] for item in tags_distribution],
            'percentages': [item['percentage'] for item in tags_distribution]
        }
    }
    
    context = {
        'total_articles': total_articles,
        'verification_distribution': verification_distribution,
        'source_distribution': source_distribution,
        'tags_distribution': tags_distribution,
        'chart_data_json': json.dumps(chart_data)
    }
    
    return render(request, 'statistics.html', context)