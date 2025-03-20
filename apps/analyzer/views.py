from django.shortcuts import render

def analyzer(request):
    return render(request, 'analyzer.html')