import folium
import geopandas as gpd
from ..abstract.stop import Stop


class MetroStation(Stop):
    
    def prepare_data(self):
        try:
            self.gdf = gpd.read_file(self.shapefile_path)
            
            # Reproyectar a WGS84
            if self.gdf.crs is None:
                self.gdf = self.gdf.set_crs("EPSG:4326", allow_override=True)
            if self.gdf.crs.to_string() != "EPSG:4326":
                self.gdf = self.gdf.to_crs("EPSG:4326")
            
            print(f"✓ Estaciones de Metro cargadas: {len(self.gdf)}")
            
        except Exception as e:
            print(f"Error preparando estaciones de Metro: {e}")
            self.gdf = None
    
    def add_to_map(self, feature_group):
        if self.gdf is None or len(self.gdf) == 0:
            return
        
        try:
            for idx, row in self.gdf.iterrows():
                # Obtener centroide si es polígono
                if row.geometry.geom_type == 'Polygon':
                    centroid = row.geometry.centroid
                    lat, lon = centroid.y, centroid.x
                else:
                    lat, lon = row.geometry.y, row.geometry.x
                
                nombre = row.get('nam', 'Estación')
                direccion = row.get('direccion', 'Sin dirección')
                
                popup_html = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4 style="margin: 0; color: #E63946;">🚇 {nombre}</h4>
                    <p style="margin: 5px 0;"><b>Dirección:</b> {direccion}</p>
                </div>
                """
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=nombre,
                    color='#E63946',
                    fill=True,
                    fillColor='white',
                    fillOpacity=1,
                    weight=3
                ).add_to(feature_group)
                
        except Exception as e:
            print(f"Error agregando estaciones del Metro al mapa: {e}")