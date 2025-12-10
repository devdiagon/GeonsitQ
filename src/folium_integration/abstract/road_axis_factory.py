from abc import ABC, abstractmethod
from .route import Route
from .stop import Stop
from .map import Map


class RoadAxisFactory(ABC):
    """Fábrica abstracta para crear componentes de sistemas de transporte"""
    
    @abstractmethod
    def create_route(self) -> Route:
        """Crea una instancia de Route"""
        pass
    
    @abstractmethod
    def create_stop(self) -> Stop:
        """Crea una instancia de Stop"""
        pass
    
    @abstractmethod
    def create_map(self) -> Map:
        """Crea una instancia de Map que integra Route y Stop"""
        pass