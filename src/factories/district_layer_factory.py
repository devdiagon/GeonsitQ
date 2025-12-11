from .map_layer_factory import MapLayerFactory
from layers.district_layer import DistrictLayer
class DistrictLayerFactory(MapLayerFactory):
    def create_layer(self, citygraph) -> DistrictLayer:
        return DistrictLayer(citygraph)
