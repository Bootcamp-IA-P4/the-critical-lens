from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('', include('apps.scraper.urls')),
    path('__reload__/', include('django_browser_reload.urls')),
]