import geopandas as gpd
import folium


class ShapefileSource:
    
    def __init__(self, shapefile_path, color_field=None):
        self.shapefile_path = shapefile_path
        self.color_field = color_field
        self.gdf = None
        self._load_data()
    
    def _load_data(self):
        try:
            self.gdf = gpd.read_file(self.shapefile_path)
            
            # Reproyectar a WGS84 para Folium
            if self.gdf.crs is None:
                print("Sin CRS, intentando inferir...")
                # Intentar diferentes CRS comunes
                if self.gdf.geometry.x.max() > 180:  # Probablemente proyectado
                    self.gdf = self.gdf.set_crs("EPSG:32717", allow_override=True)
                else:
                    self.gdf = self.gdf.set_crs("EPSG:4326", allow_override=True)
            
            if self.gdf.crs.to_string() != "EPSG:4326":
                self.gdf = self.gdf.to_crs("EPSG:4326")
            
            print(f"✓ Shapefile cargado: {len(self.gdf)} geometrías")
            
        except Exception as e:
            print(f"Error cargando shapefile: {e}")
            self.gdf = None
    
    def to_folium_geojson(self, style_function=None, tooltip_fields=None):
        """
        Convierte el GeoDataFrame a GeoJson de Folium
        
        Args:
            style_function: Función para estilizar cada feature
            tooltip_fields: Lista de campos para mostrar en tooltip
            
        Returns:
            folium.GeoJson
        """
        if self.gdf is None or len(self.gdf) == 0:
            return None
        
        try:
            # Función de estilo por defecto
            if style_function is None:
                if self.color_field and self.color_field in self.gdf.columns:
                    def style_function(feature):
                        color = feature['properties'].get(self.color_field, '#3388ff')
                        return {
                            'fillColor': color,
                            'color': 'black',
                            'weight': 0.5,
                            'fillOpacity': 0.7
                        }
                else:
                    def style_function(feature):
                        return {
                            'fillColor': '#3388ff',
                            'color': 'black',
                            'weight': 0.5,
                            'fillOpacity': 0.7
                        }
            
            # Crear tooltip
            if tooltip_fields:
                tooltip = folium.GeoJsonTooltip(
                    fields=tooltip_fields,
                    aliases=[field.replace('_', ' ').title() for field in tooltip_fields],
                    localize=True
                )
            else:
                tooltip = None
            
            # Crear GeoJson
            geojson = folium.GeoJson(
                self.gdf,
                style_function=style_function,
                tooltip=tooltip
            )
            
            return geojson
            
        except Exception as e:
            print(f"Error convirtiendo a GeoJson: {e}")
            return None
    
    def to_folium_choropleth(self, value_field, color_scheme='YlOrRd', legend_name='Valores'):
        """
        Convierte a mapa de coropletas (choropleth)
        
        Args:
            value_field: Campo numérico para colorear
            color_scheme: Esquema de colores
            legend_name: Nombre de la leyenda
            
        Returns:
            folium.Choropleth
        """
        if self.gdf is None or len(self.gdf) == 0:
            return None
        
        if value_field not in self.gdf.columns:
            print(f" Campo '{value_field}' no encontrado")
            return None
        
        try:
            choropleth = folium.Choropleth(
                geo_data=self.gdf,
                data=self.gdf,
                columns=['index', value_field],
                key_on='feature.id',
                fill_color=color_scheme,
                fill_opacity=0.7,
                line_opacity=0.5,
                legend_name=legend_name
            )
            
            return choropleth
            
        except Exception as e:
            print(f"Error creando choropleth: {e}")
            return None