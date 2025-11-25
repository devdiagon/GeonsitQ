from abstract.stop import Stop


class MetroStation(Stop):
    
    def _prepare_data(self):
        # Reproyectar a CRS
        self.gdf = self.gdf.to_crs("EPSG:32717")
        
        # Convertir polígonos a puntos (centroides)
        self.gdf_points = self.gdf.copy()
        self.gdf_points['geometry'] = self.gdf_points.geometry.centroid
        
        self.main_color = 'white'
        self.border_color = '#E63946'
    
    def visualize(self, ax=None, show_names=False):
        if ax is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(12, 10))
        
        # Dibujar estaciones
        self.gdf_points.plot(ax=ax, color=self.main_color, 
                            markersize=300, edgecolor=self.border_color, 
                            linewidth=4, zorder=12, label='Estaciones Metro')
        
        # Agregar nombres
        if show_names and 'nam' in self.gdf_points.columns:
            for idx, row in self.gdf_points.iterrows():
                ax.annotate(row['nam'], 
                           xy=(row.geometry.x, row.geometry.y),
                           xytext=(15, 10), 
                           textcoords="offset points",
                           fontsize=10, 
                           fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.5", 
                                   facecolor='white', 
                                   edgecolor=self.border_color,
                                   linewidth=2,
                                   alpha=0.95),
                           zorder=13)
        
        return ax