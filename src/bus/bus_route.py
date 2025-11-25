from abstract.route import Route


class BusRoute(Route):
    
    def __init__(self, shapefile_path, route_code='Código_Ru'):
        self.route_code = route_code
        super().__init__(shapefile_path)
    
    def _prepare_data(self):
        # Si no tiene CRS, asumir WGS84
        if self.gdf.crs is None:
            
            self.gdf = self.gdf.set_crs("EPSG:4326", allow_override=True)
        
        # Reproyectar al CRS común (EPSG:32717)
        self.gdf = self.gdf.to_crs("EPSG:32717")

        print(f"Total de líneas de bus cargadas: {len(self.gdf)}")
    
    def visualize(self, ax=None):
        if ax is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(16, 12))
        
        # Graficar directamente con categorización
        self.gdf.plot(ax=ax, column=self.route_code, categorical=True, 
                     cmap='tab20', legend=False, linewidth=2, alpha=0.7, 
                     zorder=5, label='Rutas de Buses')
        
        return ax