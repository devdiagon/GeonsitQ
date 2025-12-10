import folium
import geopandas as gpd
import numpy as np
from ..abstract.route import Route


class BusRoute(Route):
    
    def __init__(self, shapefile_path, max_routes=None):
        self.max_routes = max_routes
        self.color_map = {}
        super().__init__(shapefile_path)
    
    def prepare_data(self):
        try:
            self.gdf = gpd.read_file(self.shapefile_path)
            
            # Reproyectar a WGS84
            if self.gdf.crs is None:
                self.gdf = self.gdf.set_crs("EPSG:32717", allow_override=True)
            if self.gdf.crs.to_string() != "EPSG:4326":
                self.gdf = self.gdf.to_crs("EPSG:4326")
            
            # Limitar número de rutas si se especifica
            if self.max_routes:
                self.gdf = self.gdf.head(self.max_routes)
            
            # Generar mapa de colores
            self._generate_color_map()
            
            print(f"✓ Rutas de Buses cargadas: {len(self.gdf)}")
            
        except Exception as e:
            print(f"Error preparando rutas de Buses: {e}")
            self.gdf = None
    
    def _generate_color_map(self):
        if self.gdf is None:
            return
        
        codigos_rutas = self.gdf['Código_Ru'].unique()
        n = len(codigos_rutas)
        
        np.random.seed(42)
        colores = self._generar_colores(n)
        self.color_map = {codigo: color for codigo, color in zip(codigos_rutas, colores)}
    
    @staticmethod
    def _generar_colores(n):
        """Genera n colores distintos en formato hexadecimal para cada ruta"""
        import matplotlib.pyplot as plt
        
        if n <= 20:
            cmap = plt.cm.tab20
            colores = [cmap(i) for i in np.linspace(0, 1, n)]
        else:
            cmap1 = plt.cm.tab20
            cmap2 = plt.cm.tab20b
            n1 = min(n, 20)
            n2 = n - n1
            colores1 = [cmap1(i) for i in np.linspace(0, 1, n1)]
            colores2 = [cmap2(i) for i in np.linspace(0, 1, n2)]
            colores = colores1 + colores2
        
        colores_hex = []
        for color in colores:
            r, g, b = int(color[0]*255), int(color[1]*255), int(color[2]*255)
            colores_hex.append(f'#{r:02x}{g:02x}{b:02x}')
        
        return colores_hex
    
    def add_to_map(self, feature_group):
        if self.gdf is None or len(self.gdf) == 0:
            return
        
        try:
            for idx, row in self.gdf.iterrows():
                codigo = row['Código_Ru']
                color = self.color_map.get(codigo, '#3388ff')
                
                popup_html = f"""
                <div style="font-family: Arial;">
                    <h4 style="margin: 0;"> Ruta {codigo}</h4>
                </div>
                """
                
                geo_json = folium.GeoJson(
                    row.geometry.__geo_interface__,
                    style_function=lambda x, c=color: {
                        'color': c,
                        'weight': 2.5,
                        'opacity': 0.7
                    },
                    tooltip=f'Ruta {codigo}',
                    popup=folium.Popup(popup_html, max_width=200)
                )
                geo_json.add_to(feature_group)
                
        except Exception as e:
            print(f"Error agregando rutas al mapa: {e}")