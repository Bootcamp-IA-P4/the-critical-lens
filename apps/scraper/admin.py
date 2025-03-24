from django.contrib import admin
from .models import VerificationCategory, FactCheckArticle

@admin.register(VerificationCategory)
class VerificationCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for the VerificationCategory model.
    """
    list_display = ('name', 'description')  
    search_fields = ('name', 'description')
    list_filter = ('name',)
    readonly_fields = ('name', 'description')  

@admin.register(FactCheckArticle)
class FactCheckArticleAdmin(admin.ModelAdmin):
    """
    Admin configuration for the FactCheckArticle model.
    """
    list_display = ('title', 'verification_text', 'claim_source', 'publish_date')
    list_filter = ('verification_category',)  
    search_fields = ('title', 'claim', 'claim_source', 'content', 'tags')
    readonly_fields = ('title', 'url', 'publish_date', 'author', 'verification_category', 
                       'claim', 'claim_source', 'content', 'tags', 'scraped_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'url', 'publish_date', 'author')
        }),
        ('Verification', {
            'fields': ('verification_category', 'claim', 'claim_source')
        }),
        ('Content', {
            'fields': ('content', 'tags')
        }),
        ('Internal Control', {
            'fields': ('scraped_at',),
            'classes': ('collapse',)
        }),
    )

    def verification_text(self, obj):
        """Displays the verification category name as plain text"""
        return obj.verification_category.name if obj.verification_category else "-"
    verification_text.short_description = 'Verification'
