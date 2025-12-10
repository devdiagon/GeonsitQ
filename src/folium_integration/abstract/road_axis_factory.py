from abc import ABC, abstractmethod
from .route import Route
from .stop import Stop
from .map import Map


class RoadAxisFactory(ABC):
    
    @abstractmethod
    def create_route(self) -> Route:
        pass
    
    @abstractmethod
    def create_stop(self) -> Stop:
        pass
    
    @abstractmethod
    def create_map(self) -> Map:
        pass