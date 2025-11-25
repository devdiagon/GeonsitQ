from abstract.stop import Stop


class BusStop(Stop):
    
    def _prepare_data(self):
        # Quitar datos inválidos
        self.gdf = self.gdf[~self.gdf.geometry.is_empty]
        self.gdf = self.gdf[self.gdf.geometry.is_valid]
        
        # Asegurar CRS
        if self.gdf.crs is None:
            self.gdf = self.gdf.set_crs("EPSG:4326", allow_override=True)
        
        # Reproyectar a EPSG:32717
        self.gdf = self.gdf.to_crs("EPSG:32717")
        
        self.color_principal = 'red'
        self.color_borde = 'black'
        
        print(f"Total de paradas de bus cargadas: {len(self.gdf)}")
    
    def visualize(self, ax=None):
        if ax is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(12, 10))
        
        # Dibujar Paradas
        self.gdf.plot(ax=ax, color=self.color_principal, markersize=30, 
                     alpha=0.8, edgecolor=self.color_borde, linewidth=0.5, 
                     zorder=9, label='Paradas de Buses')
        
        return ax