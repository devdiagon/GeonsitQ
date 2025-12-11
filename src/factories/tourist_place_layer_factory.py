from .map_layer_factory import MapLayerFactory
import folium

class TouristPlaceLayerFactory(MapLayerFactory):
    def create_layer(self, citygraph):
        layers = []
        gdf = citygraph.get_tourist_places()

        # si no hay datos, no se crean capas
        if gdf is None:
            return layers

        for idx, row in gdf.iterrows():
            # ignora registros sin geometria
            if row.geometry is None:
                continue

            # nombre del lugar
            name = row.get('name', 'Lugar turistico')

            # verifica si es un centro comercial
            is_mall = (
                row.get('shop') == 'mall' or
                row.get('amenity') == 'shopping_centre'
            )

            # define colores segun el tipo
            border_color = '#ff1493' if is_mall else 'blue'
            fill_color = '#ff69b4' if is_mall else 'blue'

            try:
                # dibuja la geometria en el mapa
                layers.append(
                    folium.GeoJson(
                        row.geometry.__geo_interface__,
                        style_function=lambda x, bc=border_color, fc=fill_color: {
                            'color': bc,
                            'weight': 3 if is_mall else 2,
                            'fillColor': fc,
                            'fillOpacity': 0.6 if is_mall else 0.4
                        },
                        tooltip=name,   # muestra nombre al pasar el mouse
                        popup=name      # muestra nombre al hacer clic
                    )
                )

                # agrega marcador solo si es mall
                if is_mall and row.geometry.geom_type in ['Polygon', 'MultiPolygon', 'Point']:
                    # obtiene el centro del objeto
                    if row.geometry.geom_type == 'Point':
                        lat = row.geometry.y
                        lon = row.geometry.x
                    else:
                        center = row.geometry.centroid
                        lat = center.y
                        lon = center.x

                    # crea el marcador con icono
                    layers.append(
                        folium.Marker(
                            location=[lat, lon],
                            tooltip=f"Centro comercial: {name}",
                            popup=name,
                            icon=folium.Icon(
                                icon='shopping-cart',
                                prefix='fa',
                                color='red'
                            )
                        )
                    )

            except Exception as e:
                # si ocurre error, continua con el siguiente
                continue

        # devuelve todas las capas creadas
        return layers