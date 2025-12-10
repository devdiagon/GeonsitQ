from abc import ABC, abstractmethod

class HeatMapLayer(ABC):    
    @abstractmethod
    def to_folium_colored_polygons(self, style_function=None):
        pass