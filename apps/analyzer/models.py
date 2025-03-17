from django.db import models
from django.utils.translation import gettext_lazy as _

class VerificationCriterion(models.Model):
    """
    Analysis criterion used to evaluate news content.

    This model defines the criteria derived from EU regulations and
    Newtral's verification methodology to assess news credibility.
    """
    name = models.CharField(_('nombre'), max_length=100)
    description = models.TextField(_('descripción'))
    weight = models.FloatField(_('peso'), default=1.0)

    #Implementation details
    implementation_key = models.CharField(_('clave de implementación'), max_length=100, unique=True)

    class Meta:
        verbose_name = _('criterio de análisis')
        verbose_name_plural = _('criterios de análisis')

    def __str__(self):
        return self.name

class DatasetArticleAnalysis(models.Model):
    """
    Analysis results for a dataset article.

    This model stores the analysis results for articles from the dataset,
    which will be used for demostration and visualiuzation purposes.
    """
    # Relationship with the dataset article
    article = models.ForeignKey(
        'dataset.NewsArticle',
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name=_('artículo')
    )

    # Analysis results
    credibility_score = models.FloatField(_('puntuación de credibilidad'))
    analysis_date = models.DateTimeField(_('fecha de análisis'), auto_now_add=True)

    # Overall explanation
    summary = models.TextField(_('resumen'), blank=True)

    class Meta:
        verbose_name = _('análisis de artículo del dataset')
        verbose_name_plural = _('análisis de artículos del dataset')
        ordering = ['-analysis_date']

    def __str__(self):
        return f"Análisis de: {self.article.title[:30]}..."

class CriterionResult(models.Model):
    """
    Result for a specific criterion in an article analysis.
    
    This model stores the dailed assessment of each criterion
    for a given article analysis.
    """
    # Relationships
    analysis = models.ForeignKey(
        DatasetArticleAnalysis,
        on_delete=models.CASCADE,
        related_name='criterion_results',
        verbose_name=_('criterio')
    )

    # Results
    score = models.FloatField(_('puntuación'))
    explanation = models.TextField(_('explicación'))

    class Meta:
        verbose_name = _('resultado de criterio')
        verbose_name_plural = _('resultados de criterios')

    def __str__(self):
        return f"{self.criterion.name}: {self.score}"

