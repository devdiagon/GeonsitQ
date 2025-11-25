from abstract.route import Route


class MetroLine(Route):
    
    def _prepare_data(self):
        # Reproyectar a CRS
        self.gdf = self.gdf.to_crs("EPSG:32717")
        self.main_color = '#E63946'
        self.border_color = 'black'
    
    def visualize(self, ax=None):
        if ax is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(12, 10))
        
        # Dibujar línea con borde
        self.gdf.plot(ax=ax, color=self.border_color, linewidth=7, 
                     alpha=1, zorder=10)
        self.gdf.plot(ax=ax, color=self.main_color, linewidth=5, 
                     alpha=1, zorder=11, label='Línea Metro')
        
        return ax