from .shapefile_source import ShapefileSource
from .heatmap_layer import HeatMapLayer


class CrimesAdapter(HeatMapLayer):
    _shapefile_source = None

    def __init__(self, shapefile_path, intensity_field=None, color_field='color'):
        self.intensity_field = intensity_field
        self._shapefile_source = ShapefileSource(shapefile_path, color_field)
    
    def to_folium_colored_polygons(self, style_function=None):
        if self._shapefile_source.gdf is None or len(self._shapefile_source.gdf) == 0:
            return None
        
        try:
            if style_function is None and self._shapefile_source.color_field in self._shapefile_source.gdf.columns:
                def style_function(feature):
                    color = feature['properties'].get(self._shapefile_source.color_field, '#3388ff')
                    return {
                        'fillColor': color,
                        'color': 'black',
                        'weight': 0.5,
                        'fillOpacity': 0.7
                    }
            
            return self._shapefile_source.to_folium_geojson(style_function=style_function)
            
        except Exception as e:
            print(f"Error creando polígonos coloreados: {e}")
            return None