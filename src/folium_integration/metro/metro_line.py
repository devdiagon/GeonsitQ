import folium
import geopandas as gpd
from ..abstract.route import Route

class MetroLine(Route):
    
    def prepare_data(self):
        try:
            self.gdf = gpd.read_file(self.shapefile_path)
            
            # Reproyectar a WGS84 para Folium
            if self.gdf.crs is None:
                self.gdf = self.gdf.set_crs("EPSG:4326", allow_override=True)
            if self.gdf.crs.to_string() != "EPSG:4326":
                self.gdf = self.gdf.to_crs("EPSG:4326")
            
            print(f"✓ Línea de Metro cargada: {len(self.gdf)} geometrías")
            
        except Exception as e:
            print(f"Error preparando ruta de Metro: {e}")
            self.gdf = None
    
    def add_to_map(self, feature_group):
        if self.gdf is None or len(self.gdf) == 0:
            return
        
        try:
            for idx, row in self.gdf.iterrows():
                geo_json = folium.GeoJson(
                    row.geometry.__geo_interface__,
                    style_function=lambda x: {
                        'color': '#E63946',
                        'weight': 4,
                        'opacity': 0.9
                    },
                    tooltip='Línea de Metro'
                )
                geo_json.add_to(feature_group)
                
        except Exception as e:
            print(f"Error agregando ruta de Metro al mapa: {e}")