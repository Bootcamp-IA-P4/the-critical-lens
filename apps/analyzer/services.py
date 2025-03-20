from typing import Dict, Any

class ContentAnalysisService:
    """
    Content analysis service based on critical thinking principles.
    """
    
    def analyze_content(self, title: str, author: str, source: str, content: str) -> Dict:
        """
        Analysis of the submitted content.
        
        Args:
            title(str): The title of the content
            author(str): The author of the content
            source (str): The source of the content
            content(str): The main body of the content
            
        Returns:
            Dict with analysis results
        """
        # Initialize results dictionary
        results = {
            'overall_score': 0,
            'analysis_details': {
                'title': self._analyze_title(title),
                'author': self._analyze_author(author),
                'source': self._analyze_source(source),
                'content': self._analyze_content(content)
            }
        }
        
        # Calculate overall score
        scores = [
            results['analysis_details']['title']['score'],
            results['analysis_details']['author']['score'],
            results['analysis_details']['source']['score'],
            results['analysis_details']['content']['score']
        ]
        results['overall_score'] = sum(scores) / len(scores)
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _analyze_title(self, title: str) -> Dict[str, Any]:
        """Title analysis."""
        if not title:
            return {'score': 0, 'feedback': 'Título ausente o vacío.'}

        # Heuristic
        score = 50
        feedback = []

        if len(title) < 10:
            score -= 20
            feedback.append("Título demasiado corto")

        if len(title) > 100:
            score -= 20
            feedback.append("Título demasiado largo")

        return {
            'score': max(0, min(score, 100)),
            'feedback': ' | '.join(feedback) if feedback else 'Título aceptable'
        }
    
    def _analyze_author(self, author: str) -> Dict[str, Any]:
        """Author analysis."""
        if not author:
            return {'score': 30, 'feedback': 'Autor no identificado'}
        
        # Heuristics
        score = 70  
        feedback = []
        
        if len(author) < 2:
            score -= 40
            feedback.append('Nombre de autor poco creíble')
        
        return {
            'score': max(0, min(score, 100)),
            'feedback': ' | '.join(feedback) if feedback else 'Autor parece creíble'
        }
    
    def _analyze_source(self, source: str) -> Dict[str, Any]:
        """Source analysis."""
        if not source:
            return {'score': 30, 'feedback': 'Fuente no especificada'}
        
        # Source credibility checks
        score = 60  
        feedback = []
        
        # Expanded list of potentially credible sources
        credible_sources = [
            # International news agencies
            'reuters', 'afp', 'associated press', 'ap', 
            
            # Leading Spanish media outlets
            'el país', 'el mundo', 'la vanguardia', 'abc', 'efe', 'agencia efe', 
            'cadena ser', 'rtve', '20minutos', 
            
            # Leading Internationl media outlets
            'bbc', 'cnn', 'the guardian', 'the new york times', 'washington post', 
            'le monde', 'der spiegel', 'reuters', 'associated press', 
            
            # Verified digital media outlets
            'newtral', 'maldita.es', 'verificat.cat', 'fact-checking', 
        ]
        
        # List of sources with low credibility or potential misinformation
        low_credibility_sources = [
            # Far-right media or outlets known for misinformation
            'okdiario', 'libertad digital', 'periodista digital', 
            'caso aislado', 'alerta digital', 'la gaceta', 
            
            # Sources of conspiracies or misinformation
            'infolibre', 'vozpópuli', 'elmundo.es', 'elconfidencial', 
            
            # Highly polarized foreign media
            'fox news', 'breitbart', 'infowars', 'zerohedge', 
            
            # Unverified social media and platforms
            'facebook', 'twitter', 'instagram', 'tiktok', 'telegram', 
            'youtube', 'blog', 'foro', 'reddit'
        ]
        
        source_lower = source.lower()
        
        # Check for credible sources
        if any(credible_word in source_lower for credible_word in credible_sources):
            score += 20
            feedback.append('Fuente reconocida')
        
        # Check for low credibility sources
        if any(low_source in source_lower for low_source in low_credibility_sources):
            score -= 30
            feedback.append('Fuente con historial de desinformación')
        
        return {
            'score': max(0, min(score, 100)),
            'feedback': ' | '.join(feedback) if feedback else 'Fuente con credibilidad moderada'
        }
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Content analysis."""
        if not content:
            return {'score': 0, 'feedback': 'Contenido ausente'}
        
        # Simple content analysis
        score = 50  
        feedback = []
        
        # Check content length
        if len(content) < 50:
            score -= 30
            feedback.append('Contenido demasiado corto')
        
        # Basic check for potentially emotional language
        emotional_words = [
        # Words with extremely positive emotional charge
        'increíble', 'impresionante', 'extraordinario', 'asombroso', 'espectacular', 
        'alucinante', 'brutal', 'sensacional', 'fantástico', 'maravilloso', 
        'extraordinario', 'sublime', 'genial', 'fenomenal', 'sorprendente',
        
        # Words with extremely negative emotional charge
        'terrible', 'horrible', 'escandaloso', 'impactante', 'catastrófico', 
        'desastroso', 'trágico', 'devastador', 'horroroso', 'espantoso', 
        'apocalíptico', 'fatal', 'nefasto', 'dramático', 'perturbador',
        
        # Sensationalist terms
        'bomba', 'revolución', 'guerra', 'destrucción', 'milagro', 'locura', 
        'masacre', 'crisis', 'fracaso', 'éxito rotundo', 'golpe maestro',
        
        # Words that generate intense emotions
        'demoledor', 'fulminante', 'apabullante', 'demolición', 'absoluto', 
        'total', 'máximo', 'definitivo', 'radical', 'extremo',
        
        # Words that suggest exaggeration
        'jamás visto', 'nunca antes', 'récord', 'histórico', 'revolucionario', 
        'único', 'sin precedentes', 'inaudito', 'insólito',
        
        # Terms that appeal to strong emotions
        'miedo', 'terror', 'pánico', 'shock', 'rabia', 'indignación', 
        'odio', 'amor', 'pasión', 'ira', 'esperanza', 'desesperación',
        
        # Hyperbolic adjectives
        'supremo', 'absoluto', 'total', 'completo', 'máximo', 'supremo', 
        'definitivo', 'radical', 'extremo',
        
        # Terms suggesting conspiracy or secrecy
        'oculto', 'secreto', 'conspiración', 'manipulación', 'engaño', 
        'encubrimiento', 'filtración', 'secretismo',
        
        # Words that generate alarm or fear
        'amenaza', 'peligro', 'riesgo', 'invasión', 'colapso', 'ruina', 
        'destrucción', 'apocalipsis', 'fin', 'último',
        
        # Terms that seek to generate division or confrontation
        'guerra', 'batalla', 'lucha', 'conflicto', 'enemigo', 'traición', 
        'confrontación', 'choque', 'ruptura'
]

        emotional_count = sum(1 for word in emotional_words if word in content.lower())
        if emotional_count > 2:
            score -= 20
            feedback.append('Lenguaje potencialmente sensacionalista')
        
        return {
            'score': max(0, min(score, 100)),
            'feedback': ' | '.join(feedback) if feedback else 'Contenido aceptable'
        }
    
    
    
    def _generate_summary(self, results: Dict) -> str:
        """Generate a summary based on analysis results."""

        score = results['overall_score']
        if score >= 75:
            return "El contenido parece tener alta credibilidad según nuestros criterios."
        elif score >= 50:
            return "El contenido presenta algunos aspectos cuestionables que requieren verificación."
        else:
            return "El contenido muestra múltiples características asociadas con información dudosa."