from .map_layer_factory import MapLayerFactory
import folium

class BusStopLayerFactory(MapLayerFactory):
    def create_layer(self, citygraph):
        layers = []
        for idx, stop in citygraph.get_bus_stops().iterrows():
            geom = stop.geometry
            if geom.geom_type == "Point":
                layers.append(folium.CircleMarker(
                    location=[geom.y, geom.x],
                    radius=3,
                    popup=stop.get('name', 'Parada de bus'),
                    color='blue',
                    fill=True,
                    fillOpacity=0.7
                ))
        return layers
