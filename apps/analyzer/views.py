from django.shortcuts import render
from apps.analyzer.services import ContentAnalysisService

def analyzer(request):
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title', '')
        author = request.POST.get('author', '')
        source = request.POST.get('source', '')
        content = request.POST.get('content', '')
        
        # Perform analysis
        analyzer = ContentAnalysisService()
        results = analyzer.analyze_content(title, author, source, content)
        
        # Pass results to template
        context = {
            'results': results
        }
        return render(request, 'analyzer.html', context)
    
    # GET request, just render the form
    return render(request, 'analyzer.html')