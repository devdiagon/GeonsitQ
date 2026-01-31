from typing import Dict
from strategies.base_strategy import BaseStrategy


class ConvenienceStrategy(BaseStrategy):
    """
    Estrategia enfocada en conveniencia y acceso a servicios.
    
    Prioridades:
    1. Servicios (45%) - Centros comerciales, tiendas
    2. Transporte (35%) - Conectividad
    3. Recreación (20%) - Parques, entretenimiento
    
    Ideal para:
    - Profesionales que priorizan comodidad
    - Personas que valoran cercanía a todo
    
    Bonificaciones:
    - Distritos con todo cerca (servicios + transporte + recreación)
    """
    
    def _default_weights(self) -> Dict[str, float]:
        return {
            'services': 0.45,
            'transport': 0.35,
            'green': 0.20,
            'safety': 0.0
        }
    
    def get_name(self) -> str:
        return "Servicios y Conveniencia"
    
    def get_description(self) -> str:
        return "Maximiza acceso a comercio, transporte y recreación"
    
    def apply_bonuses(self, metrics: Dict[str, float], base_score: float) -> float:
        """
        Bonificación por tener 'todo cerca'.
        
        Si services, transport y green están todos > 0.6, bonus significativo.
        """
        services = metrics.get('services', 0.0)
        transport = metrics.get('transport', 0.0)
        green = metrics.get('green', 0.0)
        
        # Bonus por tener todo
        if services > 0.6 and transport > 0.6 and green > 0.6:
            # Distrito "completo"
            bonus = 1.2
            return min(base_score * bonus, 1.0)
        
        # Bonus menor por servicios + transporte
        if services > 0.7 and transport > 0.7:
            bonus = 1.1
            return min(base_score * bonus, 1.0)
        
        return base_score
    
    def apply_penalties(self, metrics: Dict[str, float], base_score: float) -> float:
        """
        Penalización leve si falta algún componente crítico.
        
        Si services O transport < 0.3, penalizar.
        """
        services = metrics.get('services', 0.0)
        transport = metrics.get('transport', 0.0)
        
        # Penalizar si falta acceso básico
        if services < 0.3 or transport < 0.3:
            penalty = 0.85
            return base_score * penalty
        
        return base_score