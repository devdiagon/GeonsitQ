import folium
import geopandas as gpd
import numpy as np
from ..abstract.stop import Stop


class BusStop(Stop):
    
    def __init__(self, shapefile_path, max_stops=1000):
        self.max_stops = max_stops
        super().__init__(shapefile_path)
    
    def prepare_data(self):
        try:
            self.gdf = gpd.read_file(self.shapefile_path)
            
            print(f"  Paradas originales: {len(self.gdf)}")
            
            # Limpiar datos inválidos
            self.gdf = self._clean_stops()
            
            if len(self.gdf) == 0:
                print("No hay paradas válidas después de la limpieza")
                return
            
            # Reproyectar a WGS84
            if self.gdf.crs is None:
                self.gdf = self.gdf.set_crs("EPSG:32717", allow_override=True)
            
            if self.gdf.crs.to_string() != "EPSG:4326":
                self.gdf = self.gdf.to_crs("EPSG:4326")
            
            # Verificar validez después de reproyección
            self.gdf = self._validate_coordinates()
            
            # Limitar número de paradas
            if len(self.gdf) > self.max_stops:
                self.gdf = self.gdf.head(self.max_stops)
            
            print(f"✓ Paradas de Buses cargadas: {len(self.gdf)}")
            
        except Exception as e:
            print(f"Error preparando paradas de Buses: {e}")
            import traceback
            traceback.print_exc()
            self.gdf = None
    
    def _clean_stops(self):
        gdf = self.gdf.copy()
        
        # Eliminar geometrías vacías o inválidas
        gdf = gdf[~gdf.geometry.is_empty]
        gdf = gdf[gdf.geometry.is_valid]
        
        # Filtrar por rangos válidos en CRS original (SIRES-DMQ)
        x_min, x_max = 480000, 520000
        y_min, y_max = 9960000, 10000000
        
        gdf = gdf[
            (gdf.geometry.x > x_min) & 
            (gdf.geometry.x < x_max) &
            (gdf.geometry.y > y_min) & 
            (gdf.geometry.y < y_max)
        ]
        
        return gdf
    
    def _validate_coordinates(self):
        gdf = self.gdf.copy()
        
        # Filtro adicional por coordenadas en WGS84
        gdf = gdf[
            (gdf.geometry.x > -79) & 
            (gdf.geometry.x < -78) &
            (gdf.geometry.y > -0.5) & 
            (gdf.geometry.y < 0.1)
        ]
        
        # Eliminar valores infinitos o NaN
        gdf = gdf[~gdf.geometry.x.isin([np.inf, -np.inf, np.nan])]
        gdf = gdf[~gdf.geometry.y.isin([np.inf, -np.inf, np.nan])]
        
        return gdf
    
    def add_to_map(self, feature_group):
        if self.gdf is None or len(self.gdf) == 0:
            return
        
        try:
            contador_exitoso = 0
            
            for idx, row in self.gdf.iterrows():
                try:
                    lat, lon = row.geometry.y, row.geometry.x
                    
                    # Validación adicional
                    if np.isnan(lat) or np.isnan(lon) or np.isinf(lat) or np.isinf(lon):
                        continue
                    
                    if not (-1 < lat < 1 and -79 < lon < -78):
                        continue
                    
                    principal = row.get('PRINCIPAL', 'Sin nombre')
                    secundaria = row.get('SECUNDARIA', '')
                    
                    popup_html = f"""
                    <div style="font-family: Arial; width: 220px;">
                        <h4 style="margin: 0; color: #FF6B35;">🚏 Parada</h4>
                        <p style="margin: 5px 0;"><b>Principal:</b> {principal}</p>
                        <p style="margin: 5px 0;"><b>Secundaria:</b> {secundaria}</p>
                    </div>
                    """
                    
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=4,
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=str(principal)[:50],
                        color='#FF6B35',
                        fill=True,
                        fillColor='#FF6B35',
                        fillOpacity=0.7,
                        weight=1
                    ).add_to(feature_group)
                    
                    contador_exitoso += 1
                    
                except Exception:
                    continue
            
            print(f"  ✓ {contador_exitoso} paradas agregadas al mapa")
            
        except Exception as e:
            print(f"Error agregando paradas de Bus al mapa: {e}")