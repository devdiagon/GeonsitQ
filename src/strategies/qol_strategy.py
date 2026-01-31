from typing import Dict
from strategies.base_strategy import BaseStrategy


class QualityOfLifeStrategy(BaseStrategy):
    """
    Estrategia enfocada en calidad de vida para residentes.
    
    Prioridades:
    1. Seguridad (40%)
    2. Transporte (35%)
    3. Espacios verdes (25%)
    
    Penalizaciones:
    - Zonas con seguridad muy baja (< 0.3)
    
    Bonificaciones:
    - Distritos con alta cobertura verde y buena seguridad
    """
    
    def _default_weights(self) -> Dict[str, float]:
        return {
            'safety': 0.40,
            'transport': 0.35,
            'green': 0.25,
            'services': 0.0
        }
    
    def get_name(self) -> str:
        return "Calidad de Vida"
    
    def get_description(self) -> str:
        return "Prioriza seguridad, acceso a transporte y espacios verdes para residentes"
    
    def apply_penalties(self, metrics: Dict[str, float], base_score: float) -> float:
        """
        Aplica penalizaciones por baja seguridad.
        
        Si safety < 0.3 (zona muy insegura), penalizar score.
        """
        safety = metrics.get('safety', 0.5)
        
        if safety < 0.3:
            # Penalización del 20% si es muy inseguro
            penalty = 0.8
            return base_score * penalty
        
        return base_score
    
    def apply_bonuses(self, metrics: Dict[str, float], base_score: float) -> float:
        """
        Aplica bonificaciones por excelencia en seguridad + verde.
        
        Si safety > 0.8 Y green > 0.6, dar bonus del 10%.
        """
        safety = metrics.get('safety', 0.0)
        green = metrics.get('green', 0.0)
        
        if safety > 0.8 and green > 0.6:
            # Bonus del 10% por combinación ideal
            bonus = 1.1
            return min(base_score * bonus, 1.0)
        
        return base_score