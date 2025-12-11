from abc import ABC, abstractmethod


class MapLayer(ABC):
    
    def __init__(self, citygraph):
        self.citygraph = citygraph
        self.elements = []
        self._build_layer()
    
    @abstractmethod
    def _build_layer(self):
        pass
    
    def get_elements(self):
        return self.elements
    
    def add_to_map(self, folium_map):
        for element in self.elements:
            element.add_to(folium_map)
    
    def add_to_feature_group(self, feature_group):
        for element in self.elements:
            element.add_to(feature_group)
    
    def get_layer_name(self):
        return self.__class__.__name__.replace('Layer', '')