import matplotlib.pyplot as plt
from abstract.map import Map


class BusMap(Map):
    
    def visualize(self, ax=None, titulo="Sistema de Buses Urbanos"):
        if ax is None:
            fig, ax = plt.subplots(figsize=(16, 12))
            show = True
        else:
            show = False
        
        # Visualizar rutas y paradas
        self.route.visualize(ax)
        self.stop.visualize(ax)
        
        if show:
            plt.title(titulo, fontsize=18, fontweight='bold')
            plt.xlabel('X (metros UTM)', fontsize=12)
            plt.ylabel('Y (metros UTM)', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend(loc='upper right', fontsize=11)
            plt.tight_layout()
            plt.show()
        
        return ax