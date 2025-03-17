# apps/analyzer/services.py
from typing import Dict, List, Tuple, Optional

class ContentAnalysisService:
    """
    Service for analyzing content without persisting it.
    
    This service applies the same analysis criteria used for dataset articles
    but works with transient user-submitted content that won't be stored.
    """
    
    def __init__(self, criteria=None):
        """
        Initialize with available criteria.
        
        Args:
            criteria: List of AnalysisCriterion instances to use
        """
        from .models import AnalysisCriterion
        self.criteria = criteria or list(AnalysisCriterion.objects.all())
    
    def analyze_content(self, title: str, content: str) -> Dict:
        """
        Analyze user-submitted content without storing it.
        
        Args:
            title: The title of the content
            content: The main body of the content
            
        Returns:
            Dictionary with analysis results including:
            - overall_score: float
            - criteria_results: list of dicts with criterion results
            - summary: text summary of the analysis
        """
        results = {
            'overall_score': 0,
            'criteria_results': [],
            'summary': ''
        }
        
        total_weight = sum(criterion.weight for criterion in self.criteria)
        weighted_score = 0
        
        for criterion in self.criteria:
            # Get implementation class based on criterion key
            analyzer = self._get_analyzer_for_criterion(criterion.implementation_key)
            
            # Apply the criterion to the content
            score, explanation = analyzer.analyze(title, content)
            
            # Store results
            results['criteria_results'].append({
                'criterion_name': criterion.name,
                'criterion_description': criterion.description,
                'score': score,
                'explanation': explanation
            })
            
            # Update weighted score
            weighted_score += score * criterion.weight
        
        # Calculate overall score
        if total_weight > 0:
            results['overall_score'] = weighted_score / total_weight
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _get_analyzer_for_criterion(self, implementation_key: str):
        """Get the appropriate analyzer implementation for a criterion."""
        # This would be implemented to return the correct analyzer class
        # based on the implementation_key
        from .criteria import get_criterion_analyzer
        return get_criterion_analyzer(implementation_key)
    
    def _generate_summary(self, results: Dict) -> str:
        """Generate a summary based on analysis results."""
        # Simple summary generation
        score = results['overall_score']
        if score >= 75:
            return "El contenido parece tener alta credibilidad según nuestros criterios."
        elif score >= 50:
            return "El contenido presenta algunos aspectos cuestionables que requieren verificación."
        else:
            return "El contenido muestra múltiples características asociadas con información dudosa."