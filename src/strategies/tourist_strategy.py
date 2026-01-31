from typing import Dict
from strategies.base_strategy import BaseStrategy


class TouristStrategy(BaseStrategy):
    """
    Estrategia enfocada en turistas y visitantes.
    
    Prioridades:
    1. Servicios (40%) - Centros comerciales, museos, atracciones
    2. Seguridad (35%)
    3. Transporte (25%) - Facilidad de movilidad
    
    Bonificaciones:
    - Distritos con alta concentración de servicios turísticos
    - Presencia de metro (movilidad premium)
    
    Penalizaciones:
    - Zonas inseguras para turistas
    """
    
    def _default_weights(self) -> Dict[str, float]:
        return {
            'services': 0.40,
            'safety': 0.35,
            'transport': 0.25,
            'green': 0.0
        }
    
    def get_name(self) -> str:
        return "Turista/Visitante"
    
    def get_description(self) -> str:
        return "Enfoca en atractivos turísticos, seguridad y facilidad de movilidad"
    
    def apply_penalties(self, metrics: Dict[str, float], base_score: float) -> float:
        """
        Penaliza zonas inseguras (turistas son más vulnerables).
        
        Si safety < 0.4, penalización más agresiva que otras estrategias.
        """
        safety = metrics.get('safety', 0.5)
        
        if safety < 0.4:
            # Penalización del 30% (más severa que para residentes)
            penalty = 0.7
            return base_score * penalty
        elif safety < 0.6:
            # Penalización leve
            penalty = 0.9
            return base_score * penalty
        
        return base_score
    
    def apply_bonuses(self, metrics: Dict[str, float], base_score: float) -> float:
        """
        Bonificación por alta concentración de servicios turísticos.
        
        Si services > 0.7, dar bonus del 15%.
        """
        services = metrics.get('services', 0.0)
        transport = metrics.get('transport', 0.0)
        
        # Bonus por muchos servicios
        if services > 0.7:
            bonus = 1.15
            return min(base_score * bonus, 1.0)
        
        # Bonus por excelente transporte (metro)
        if transport > 0.8:
            bonus = 1.1
            return min(base_score * bonus, 1.0)
        
        return base_score