from typing import Dict, Optional
import yaml

from strategies.base_strategy import BaseStrategy
from strategies.qol_strategy import QualityOfLifeStrategy
from strategies.tourist_strategy import TouristStrategy
from strategies.convenience_strategy import ConvenienceStrategy


class StrategyFactory:    
    _STRATEGIES = {
        'quality_of_life': QualityOfLifeStrategy,
        'tourist': TouristStrategy,
        'convenience': ConvenienceStrategy,
    }
    
    @classmethod
    def create_strategy(
        cls,
        strategy_name: str,
        config: Optional[Dict] = None
    ) -> BaseStrategy:
        """
        Crea una instancia de estrategia por nombre.
        
        Args:
            strategy_name: Nombre de la estrategia
                          ('quality_of_life', 'tourist', 'convenience')
            config: Configuración específica (opcional)
        
        Returns:
            Instancia de BaseStrategy
        
        Raises:
            ValueError: Si el nombre de estrategia no existe
        
        Example:
            >>> strategy = StrategyFactory.create_strategy('quality_of_life')
            >>> score = strategy.calculate_final_score(metrics)
        """
        if strategy_name not in cls._STRATEGIES:
            available = ', '.join(cls._STRATEGIES.keys())
            raise ValueError(
                f"Estrategia '{strategy_name}' no existe. "
                f"Disponibles: {available}"
            )
        
        strategy_class = cls._STRATEGIES[strategy_name]
        return strategy_class(config=config)
    
    @classmethod
    def create_all_strategies(
        cls,
        config_path: str = 'config.yaml'
    ) -> Dict[str, BaseStrategy]:
        """
        Crea todas las estrategias desde archivo de configuración.
        
        Args:
            config_path: Ruta al archivo config.yaml
        
        Returns:
            Dict con nombre → instancia de estrategia
        
        Example:
            >>> strategies = StrategyFactory.create_all_strategies()
            >>> for name, strategy in strategies.items():
            ...     print(f"{name}: {strategy.get_description()}")
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f" Error cargando config: {e}")
            config = {}
        
        strategies_config = config.get('strategies', {})
        strategies = {}
        
        for name, strategy_class in cls._STRATEGIES.items():
            strategy_config = strategies_config.get(name, {})
            strategies[name] = strategy_class(config=strategy_config)
        
        return strategies
    
    @classmethod
    def get_available_strategies(cls) -> list:
        return list(cls._STRATEGIES.keys())