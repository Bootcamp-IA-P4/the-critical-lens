from django.db import models
from django.utils.translation import gettext_lazy as _

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
    image_url = models.URLField(_('URL de la imagen'), blank=True)
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