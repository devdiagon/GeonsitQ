import folium
from .map_layer import MapLayer


class TouristPlaceLayer(MapLayer):
    
    def _build_layer(self):
        gdf = self.citygraph.get_tourist_places()
        
        # Si no hay datos, no se crean elementos
        if gdf is None:
            return
        
        for idx, row in gdf.iterrows():
            # Ignorar registros sin geometría
            if row.geometry is None:
                continue
            
            # Nombre del lugar
            name = row.get('name', 'Lugar turístico')
            
            # Verificar si es un centro comercial
            is_mall = (
                row.get('shop') == 'mall' or
                row.get('amenity') == 'shopping_centre'
            )
            
            # Definir colores según el tipo
            border_color = '#ff1493' if is_mall else 'blue'
            fill_color = '#ff69b4' if is_mall else 'blue'
            
            try:
                # Dibujar la geometría en el mapa
                geojson = folium.GeoJson(
                    row.geometry.__geo_interface__,
                    style_function=lambda x, bc=border_color, fc=fill_color, im=is_mall: {
                        'color': bc,
                        'weight': 3 if im else 2,
                        'fillColor': fc,
                        'fillOpacity': 0.6 if im else 0.4
                    },
                    tooltip=name,
                    popup=name
                )
                self.elements.append(geojson)
                
                # Agregar marcador solo si es mall
                if is_mall and row.geometry.geom_type in ['Polygon', 'MultiPolygon', 'Point']:
                    # Obtener el centro del objeto
                    if row.geometry.geom_type == 'Point':
                        lat = row.geometry.y
                        lon = row.geometry.x
                    else:
                        center = row.geometry.centroid
                        lat = center.y
                        lon = center.x
                    
                    # Crear el marcador con icono
                    marker = folium.Marker(
                        location=[lat, lon],
                        tooltip=f"Centro comercial: {name}",
                        popup=name,
                        icon=folium.Icon(
                            icon='shopping-cart',
                            prefix='fa',
                            color='red'
                        )
                    )
                    self.elements.append(marker)
                    
            except Exception as e:
                # Si ocurre error, continuar con el siguiente
                continue
    
    def get_layer_name(self):
        return " Lugares Turísticos"