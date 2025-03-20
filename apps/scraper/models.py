from django.db import models
from django.utils.translation import gettext_lazy as _
import re
from datetime import datetime

class VerificationCategory(models.Model):
    """
    Verfication category used by Newtral (e.g., "Falso", "Engañoso").

    This model stores the different verification labels taht Newtral
    uses in their fact checking artiicles.
    """

    name = models.CharField(_('nombre'), max_length=50)
    description = models.TextField(_('descripción'), blank=True)
    color = models.CharField(_('color'), max_length=7, default='#CCCCCC')

    class Meta:
        verbose_name = _('categoría de verificación')
        verbose_name_plural = _('categorías de verificación')

    def __str__(self):
        return self.name

class FactCheckArticle(models.Model):
    """
    Fact checking article scraped from Newtral.
    
    This model stores essential information from Newtral fact-checks,
    which will be used to establish verification criteria alongside EU regulations.
    """
    # Basic information
    title = models.CharField(_('título'), max_length=255)
    url = models.URLField(_('URL'), unique=True)
    publish_date = models.DateField(_('fecha de publicación'), null=True, blank=True)

    # Categorization
    verification_category = models.ForeignKey(
        VerificationCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name=_('categoría de verificación')
    )

    # Main content
    claim = models.TextField(_('afirmación verificada'))
    claim_source = models.CharField(_('fuente de la afirmación'), max_length=255)
    content = models.TextField(_('contenido'))

    # Media and metadata
    tags = models.CharField(_('etiquetas'), max_length=255, blank=True)
    author = models.CharField(_('autor'), max_length=100, blank=True)

    # Internal control
    scraped_at = models.DateTimeField(_('fecha de extracción'), auto_now_add=True)
    is_processed = models.BooleanField(_('procesado'), default=False)

    class Meta:
        verbose_name = _('artículo de verificación')
        verbose_name_plural = _('artículos de verificación')
        ordering = ['-publish_date', '-scraped_at']

    def __str__(self):
        return self.title
        
    @classmethod
    def parse_date(cls, date_str):
        """
        Parse dates from Newtral articles into a standard date format.
        
        Args:
            date_str: String containing a date
                
        Returns:
            datetime.date or None if parsing fails
        """
        if not date_str:
            return None
                
        # Convert datetime to date
        if hasattr(date_str, 'date'):
            return date_str.date()
                
        # Convert to string and clean
        if not isinstance(date_str, str):
            date_str = str(date_str)
        
        date_str = date_str.strip()
        
        # Try to extract date from URL (Newtral format: /YYYYMMDD/)
        url_match = re.search(r'/(\d{8})/', date_str)
        if url_match:
            try:
                year = int(url_match.group(1)[:4])
                month = int(url_match.group(1)[4:6])
                day = int(url_match.group(1)[6:8])
                return datetime(int(year), int(month), int(day)).date()
            except (ValueError, IndexError):
                pass
                    
        # Try Spanish format with improved regex
        spanish_months = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
            "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
            "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
        }
        
        spanish_match = re.search(r'(\d{1,2})\s+de\s+(\w+)(?:\s+de\s+|\s+)(\d{4})', date_str.lower())
        if spanish_match:
            try:
                day = int(spanish_match.group(1))
                month = spanish_months.get(spanish_match.group(2))
                year = int(spanish_match.group(3))
                if month:
                    return datetime(year, month, day).date()
            except (ValueError, IndexError):
                pass
        
        # Try ISO format (YYYY-MM-DD)
        iso_match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_str)
        if iso_match:
            try:
                year = int(iso_match.group(1))
                month = int(iso_match.group(2))
                day = int(iso_match.group(3))
                return datetime(year, month, day).date()
            except (ValueError, TypeError):
                pass
        
        # Try direct parsing with dateutil as a last resort
        try:
            from dateutil import parser
            return parser.parse(date_str).date()
        except:
            pass
        
        return None