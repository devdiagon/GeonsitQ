from typing import Optional, Dict
import pandas as pd

from observers.map_state import Observer, MapState
from analyzers.district_analyzer import DistrictAnalyzer


class RecommendationObserver(Observer):    
    def __init__(self, district_analyzer: DistrictAnalyzer):
        self.analyzer = district_analyzer
        self.current_scores: Optional[pd.DataFrame] = None
        self.current_strategy_name: Optional[str] = None
    
    def update(self, state: MapState, change_type: str, **kwargs):
        """
        Maneja cambios de estado.
        
        Args:
            state: Estado del mapa
            change_type: Tipo de cambio
            **kwargs: Datos adicionales del cambio
        """
        # Solo reaccionar a cambios de estrategia
        if change_type == 'strategy':
            self._handle_strategy_change(state, **kwargs)
        elif change_type == 'reset':
            self._handle_reset()
    
    def _handle_strategy_change(self, state: MapState, **kwargs):
        """
        Maneja cambio de estrategia.
        
        Recalcula todos los scores con la nueva estrategia.
        """
        new_strategy = kwargs.get('new_strategy')
        
        if new_strategy is None:
            print(" RecommendationObserver: Nueva estrategia es None")
            return
        
        print(f"\nRecommendationObserver: Recalculando scores...")
        print(f"   Estrategia: {new_strategy.get_name()}")
        
        # Obtener métricas del analyzer
        if self.analyzer.metrics_df is None:
            print("No hay métricas disponibles en el analyzer")
            return
        
        metrics_df = self.analyzer.metrics_df
        
        # Calcular scores con la nueva estrategia
        scores = []
        for idx, row in metrics_df.iterrows():
            metrics_dict = {
                'safety': row['safety'],
                'transport': row['transport'],
                'green': row['green'],
                'services': row['services']
            }
            
            score = new_strategy.calculate_final_score(metrics_dict)
            scores.append(score)
        
        # Crear DataFrame con scores
        self.current_scores = metrics_df.copy()
        self.current_scores['score'] = scores
        self.current_scores['rank'] = self.current_scores['score'].rank(
            ascending=False,
            method='min'
        ).astype(int)
        
        # Ordenar por score
        self.current_scores = self.current_scores.sort_values(
            'score',
            ascending=False
        ).reset_index(drop=True)
        
        self.current_strategy_name = new_strategy.get_name()
        
        print(f"Scores recalculados:")
        print(f"   Top distrito: {self.current_scores.iloc[0]['district_name']} "
              f"(score: {self.current_scores.iloc[0]['score']:.3f})")
        print(f"   Promedio: {self.current_scores['score'].mean():.3f}")
    
    def _handle_reset(self):
        print("\nRecommendationObserver: Limpiando scores...")
        self.current_scores = None
        self.current_strategy_name = None
    
    def get_scores_df(self) -> Optional[pd.DataFrame]:
        return self.current_scores
    
    def get_top_districts(self, n: int = 5) -> Optional[pd.DataFrame]:
        if self.current_scores is None:
            return None
        
        return self.current_scores.head(n)[
            ['district_name', 'score', 'rank', 'safety', 'transport', 'green', 'services']
        ]
    
    def get_district_score(self, district_name: str) -> Optional[Dict]:
        """
        Obtiene score y detalles de un distrito específico.
        
        Args:
            district_name: Nombre del distrito
        
        Returns:
            Dict con score y métricas o None si no existe
        """
        if self.current_scores is None:
            return None
        
        district = self.current_scores[
            self.current_scores['district_name'] == district_name
        ]
        
        if len(district) == 0:
            return None
        
        district = district.iloc[0]
        
        return {
            'name': district['district_name'],
            'score': district['score'],
            'rank': district['rank'],
            'metrics': {
                'safety': district['safety'],
                'transport': district['transport'],
                'green': district['green'],
                'services': district['services']
            }
        }