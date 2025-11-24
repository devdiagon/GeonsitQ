from .map_layer_factory import MapLayerFactory
import folium

class DistrictLayerFactory(MapLayerFactory):
    def create_layer(self, citygraph):
        layers = []
        for idx, row in citygraph.get_graph().iterrows():
            layers.append(folium.GeoJson(
                row.geometry.__geo_interface__,
                style_function=lambda x: {'fillColor': 'red', 'color': 'red', 'weight': 2, 'fillOpacity': 0.1},
                popup=row.get('display_name', 'N/A')
            ))
        return layers
