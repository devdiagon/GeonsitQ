from abc import ABC, abstractmethod

class MapLayerFactory(ABC):
    @abstractmethod
    def create_layer(self, citygraph):
        pass
