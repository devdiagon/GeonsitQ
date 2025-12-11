from .map_layer_factory import MapLayerFactory
from layers.tourist_place_layer import TouristPlaceLayer

class TouristPlaceLayerFactory(MapLayerFactory):
    def create_layer(self, citygraph) -> TouristPlaceLayer:
        return TouristPlaceLayer(citygraph)