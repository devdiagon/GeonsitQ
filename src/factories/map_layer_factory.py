from abc import ABC, abstractmethod
from layers.map_layer import MapLayer

class MapLayerFactory(ABC):
    @abstractmethod
    def create_layer(self, citygraph) -> MapLayer:
        pass
    
    def create_feature_group(self, citygraph):
        import folium
        
        layer = self.create_layer(citygraph)
        feature_group = folium.FeatureGroup(name=layer.get_layer_name())
        layer.add_to_feature_group(feature_group)
        
        return feature_group
