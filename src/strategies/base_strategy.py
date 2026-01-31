from abc import ABC, abstractmethod
from typing import Dict, Optional
import pandas as pd


class BaseStrategy(ABC):    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._weights = self._default_weights()
        
        if 'weights' in self.config:
            self._weights.update(self.config['weights'])
    
    @abstractmethod
    def _default_weights(self) -> Dict[str, float]:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        pass
    
    def get_weights(self) -> Dict[str, float]:
        return self._weights.copy()
    
    def calculate_score(self, metrics: Dict[str, float]) -> float:
        """
        Calcula el score final basado en las métricas del distrito.
        
        Args:
            metrics: Dict con métricas del distrito
                    (ej: {'safety': 0.8, 'transport': 0.6, ...})
        
        Returns:
            float: Score final (0.0 - 1.0)
        """
        total_score = 0.0
        total_weight = 0.0
        
        for metric, weight in self._weights.items():
            if metric in metrics:
                value = metrics[metric]
                
                # Validar que el valor es numérico
                if pd.notna(value):
                    total_score += value * weight
                    total_weight += weight
        
        # Normalizar por el peso total disponible
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.0
        
        return final_score
    
    def apply_penalties(self, metrics: Dict[str, float], base_score: float) -> float:
        """
        Aplica penalizaciones al score base según criterios de la estrategia.
        
        Args:
            metrics: Dict con métricas del distrito
            base_score: Score base calculado
        
        Returns:
            float: Score ajustado después de penalizaciones
        
        Note:
            Las estrategias pueden sobrescribir este método para aplicar
            penalizaciones específicas (ej: penalizar zonas inseguras)
        """
        return base_score
    
    def apply_bonuses(self, metrics: Dict[str, float], base_score: float) -> float:
        """
        Aplica bonificaciones al score base según criterios de la estrategia.
        
        Args:
            metrics: Dict con métricas del distrito
            base_score: Score base calculado
        
        Returns:
            float: Score ajustado después de bonificaciones
        
        Note:
            Las estrategias pueden sobrescribir este método para aplicar
            bonificaciones específicas (ej: bonus por tener metro)
        """
        return base_score
    
    def calculate_final_score(self, metrics: Dict[str, float]) -> float:
        """
        Calcula el score final aplicando pesos, bonificaciones y penalizaciones.
        
        Este es el método principal que deben usar los clientes.
        
        Args:
            metrics: Dict con métricas del distrito
        
        Returns:
            float: Score final (0.0 - 1.0)
        """
        # Calcular score base
        base_score = self.calculate_score(metrics)
        
        # Aplicar penalizaciones
        score_with_penalties = self.apply_penalties(metrics, base_score)
        
        # Aplicar bonificaciones
        final_score = self.apply_bonuses(metrics, score_with_penalties)
        
        # Asegurar que está en rango [0, 1]
        final_score = max(0.0, min(1.0, final_score))
        
        return final_score
    
    def get_color_scheme(self) -> str:
        """
        Retorna el esquema de colores para visualización.
        
        Returns:
            str: Nombre del esquema de colores (ej: 'YlGn', 'RdYlGn')
        """
        return self.config.get('color_scheme', 'YlGn')
    
    def __str__(self) -> str:
        return f"{self.get_name()} - {self.get_description()}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(weights={self._weights})"