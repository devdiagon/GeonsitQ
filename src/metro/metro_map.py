import matplotlib.pyplot as plt
from abstract.map import Map


class MetroMap(Map):
    
    def visualize(self, ax=None, show_names=True, title="Sistema Metro"):
        if ax is None:
            fig, ax = plt.subplots(figsize=(16, 12))
            show = True
        else:
            show = False
        
        # visualizar línea y estaciones
        self.route.visualize(ax)
        self.stop.visualize(ax, show_names)
        
        if show:
            plt.title(title, fontsize=18, fontweight='bold')
            plt.xlabel('X (metros UTM)', fontsize=12)
            plt.ylabel('Y (metros UTM)', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend(loc='upper right', fontsize=11)
            plt.tight_layout()
            plt.show()
        
        return ax