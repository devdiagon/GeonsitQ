import folium
from .map_layer import MapLayer


class DistrictLayer(MapLayer):
    
    def _build_layer(self):
        graph = self.citygraph.get_graph()
        
        if graph is None:
            return
        
        for idx, row in graph.iterrows():
            geojson = folium.GeoJson(
                row.geometry.__geo_interface__,
                style_function=lambda x: {
                    'fillColor': 'red',
                    'color': 'red',
                    'weight': 2,
                    'fillOpacity': 0.1
                },
                popup=row.get('display_name', 'N/A'),
                tooltip=row.get('display_name', 'Distrito')
            )
            self.elements.append(geojson)
    
    def get_layer_name(self):
        return " Distritos"