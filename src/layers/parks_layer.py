import folium
from .map_layer import MapLayer


class ParksLayer(MapLayer):
    
    def _build_layer(self):
        parks = self.citygraph.get_parks()
        
        if parks is None:
            return
        
        for idx, row in parks.iterrows():
            geom = row.geometry
            popup_text = row.get('name', 'Parque')
            
            if geom.geom_type == 'Point':
                # Crear marcador para punto
                icon = folium.Icon(color='green', icon='tree', prefix='fa')
                
                marker = folium.Marker(
                    location=[geom.y, geom.x],
                    icon=icon,
                    popup=popup_text,
                    tooltip="Ver parque"
                )
                self.elements.append(marker)
            else:
                # Crear GeoJson para polígonos
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
                self.elements.append(geojson)
    
    def get_layer_name(self):
        return " Parques"