from .map_layer_factory import MapLayerFactory
import folium

class ParksLayerFactory(MapLayerFactory):
    def create_layer(self, citygraph):
        layers = []
        parks = citygraph.get_parks()
        if parks is None:
            return layers
        for idx, row in parks.iterrows():
            geom = row.geometry
            popup_text = row.get('name', 'Parque')
            if geom.geom_type == 'Point':
                icon = folium.Icon(color='green', icon='tree', prefix='fa')
                
                marker = folium.Marker(
                    location=[geom.y, geom.x],
                    icon=icon,
                    popup=popup_text,
                    tooltip="Ver parque"
                )
                layers.append(marker)
            else:
                geojson = folium.GeoJson(
                    geom.__geo_interface__,
                    style_function=lambda x: {
                        'fillColor': '#2E8B57',  
                        'color': '#228B22',      
                        'weight': 1,
                        'fillOpacity': 0.6
                    },
                    popup=popup_text,
                    tooltip=popup_text
                )
                layers.append(geojson)
        return layers