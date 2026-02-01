from typing import Dict, Optional
import pandas as pd

from mapq import CityGraph
from analyzers.district_analyzer import DistrictAnalyzer
from strategies.strategy_factory import StrategyFactory
from strategies.base_strategy import BaseStrategy
from observers.map_state import MapState
from observers.recommendation_observer import RecommendationObserver
from observers.cache_observer import CacheObserver


class RecommendationSystem:
    """    
    Responsabilidades:
    - Inicializar CityGraph
    - Configurar DistrictAnalyzer
    - Gestionar estrategias
    - Coordinar observers
    - Proporcionar interfaz simple para UI (Streamlit)
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Inicializa el sistema de recomendaciones.
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        
        # Cargar datos con CityGraph
        self.city = CityGraph()
        
        # Crear analyzer
        print("\nConfigurando analizador de distritos...")
        self.analyzer = DistrictAnalyzer(config_path=config_path)
        self.analyzer.load_data(
            districts_gdf=self.city.get_graph(),
            parks_gdf=self.city.get_parks(),
            tourist_places_gdf=self.city.get_tourist_places()
        )
        
        # Cargar estrategias
        self.strategies = StrategyFactory.create_all_strategies(config_path)
        self.current_strategy_name = None
        
        # Crear estado observable
        self.map_state = MapState()
        
        # Crear observers
        self.rec_observer = RecommendationObserver(self.analyzer)
        self.cache_observer = CacheObserver(self.analyzer)
        
        # Registrar observers
        self.map_state.attach(self.rec_observer)
        self.map_state.attach(self.cache_observer)
        
        # Analizar distritos (con caché)
        self.metrics_df = self.analyzer.analyze_all_districts(force_refresh=False)
        
        print(f"   Distritos: {len(self.metrics_df)}")
        print(f"   Estrategias: {len(self.strategies)}")
    
    def set_strategy(self, strategy_name: str) -> bool:
        """
        Cambia la estrategia de análisis.
        
        Args:
            strategy_name: Nombre de la estrategia
                          ('quality_of_life', 'tourist', 'convenience')
        
        Returns:
            bool: True si se cambió exitosamente
        """
        if strategy_name not in self.strategies:
            available = ', '.join(self.strategies.keys())
            print(f"Estrategia '{strategy_name}' no existe. Disponibles: {available}")
            return False
        
        strategy = self.strategies[strategy_name]
        self.map_state.set_strategy(strategy)
        self.current_strategy_name = strategy_name
        
        return True
    
    def get_current_strategy(self) -> Optional[BaseStrategy]:
        return self.map_state.current_strategy
    
    def get_scores_df(self) -> Optional[pd.DataFrame]:
        return self.rec_observer.get_scores_df()
    
    def get_top_districts(self, n: int = 5) -> Optional[pd.DataFrame]:
        return self.rec_observer.get_top_districts(n)
    
    def get_district_details(self, district_name: str) -> Optional[Dict]:
        return self.rec_observer.get_district_score(district_name)
    
    def get_available_strategies(self) -> Dict[str, str]:
        return {
            name: strategy.get_description()
            for name, strategy in self.strategies.items()
        }
    
    def get_metrics_df(self) -> pd.DataFrame:
        return self.metrics_df
    
    def get_system_status(self) -> Dict:
        cache_info = self.analyzer.get_cache_info()
        
        return {
            'num_districts': len(self.metrics_df),
            'current_strategy': self.current_strategy_name,
            'available_strategies': list(self.strategies.keys()),
            'cache_enabled': cache_info.get('enabled', False),
            'cache_valid': cache_info.get('is_valid', False),
            'observers_active': len(self.map_state._observers),
        }
    
    def invalidate_cache(self):
        self.analyzer.invalidate_cache()
    
    def refresh_analysis(self):
        self.metrics_df = self.analyzer.analyze_all_districts(force_refresh=True)
        
        # Re-calcular scores si hay estrategia activa
        if self.current_strategy_name:
            self.set_strategy(self.current_strategy_name)
    
    def create_map(self, **kwargs):
        return self.city.create_map(**kwargs)