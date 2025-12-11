from .map_layer_factory import MapLayerFactory
from layers.parks_layer import ParksLayer

class ParksLayerFactory(MapLayerFactory):
    def create_layer(self, citygraph) -> ParksLayer:
        return ParksLayer(citygraph)