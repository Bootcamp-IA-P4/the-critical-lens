from django.db import models
from django.utils.translation import gettext_lazy as _

class VerificationCriterion(models.Model):
    """
    Abstract and extensible content verification criteria.
    
    Allows defining flexible verification criteria for content analysis,
    with the ability to weight and activate/deactivate specific criteria.
    
    Attributes:
        name (str): Name of the verification criterion.
        description (str): Detailed description of the criterion.
        weight (float): Importance weight of the criterion in overall analysis.
        implementation_key (str): Unique key to identify specific implementation strategies.
        is_active (bool): Indicates whether the criterion is active for analysis.
    """
    name = models.CharField(_('nombre'), max_length=100)
    description = models.TextField(_('descripción'))
    weight = models.FloatField(_('peso'), default=1.0)
    
    implementation_key = models.CharField(
        _('clave de implementación'), 
        max_length=100, 
        unique=True
    )
    
    is_active = models.BooleanField(_('activo'), default=True)

    class Meta:
        verbose_name = _('criterio de verificación')
        verbose_name_plural = _('criterios de verificación')

    def __str__(self):
        return self.name

class ContentAnalysis(models.Model):
    """
    Temporary model to store and analyze user-submitted content.
    
    Captures the content submitted by users for credibility analysis,
    providing a mechanism to evaluate and score user-provided articles.
    
    Attributes:
        title (str): Title of the article submitted by the user.
        content (str): Full text content of the article.
        author (str, optional): Author of the content.
        source (str, optional): Source of the content.
        credibility_score (float, optional): Overall credibility score of the content.
        analysis_date (datetime): Timestamp of the analysis.
        summary (str, optional): Summary of the analysis results.
    """
    title = models.CharField(_('título'), max_length=255)
    content = models.TextField(_('contenido'))
    author = models.CharField(_('autor'), max_length=100, blank=True, null=True)
    source = models.CharField(_('fuente'), max_length=200, blank=True, null=True)
    
    credibility_score = models.FloatField(_('puntuación de credibilidad'), null=True, blank=True)
    analysis_date = models.DateTimeField(_('fecha de análisis'), auto_now_add=True)
    summary = models.TextField(_('resumen'), blank=True)

    class Meta:
        verbose_name = _('análisis de contenido')
        verbose_name_plural = _('análisis de contenido')
        ordering = ['-analysis_date']

    def __str__(self):
        return f"Análisis de: {self.title[:50]}"

class CriterionResult(models.Model):
    """
    Individual criterion results for a specific content analysis.
    
    Stores the detailed results of each verification criterion applied 
    to a specific content analysis, allowing granular insight into 
    how different criteria contribute to the overall credibility assessment.
    
    Attributes:
        analysis (ContentAnalysis): The content analysis this result belongs to.
        criterion (VerificationCriterion): The specific verification criterion applied.
        score (float): Score achieved by this criterion.
        explanation (str): Detailed explanation of the criterion's evaluation.
    """
    analysis = models.ForeignKey(
        ContentAnalysis, 
        on_delete=models.CASCADE, 
        related_name='criterion_results',
        verbose_name=_('análisis')
    )
    
    criterion = models.ForeignKey(
        VerificationCriterion, 
        on_delete=models.CASCADE,
        verbose_name=_('criterio')
    )
    
    score = models.FloatField(_('puntuación'))
    explanation = models.TextField(_('explicación'))

    class Meta:
        verbose_name = _('resultado de criterio')
        verbose_name_plural = _('resultados de criterios')
        unique_together = ['analysis', 'criterion']

    def __str__(self):
        return f"{self.criterion.name}: {self.score}"