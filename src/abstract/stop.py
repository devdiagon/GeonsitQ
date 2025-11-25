from abc import ABC, abstractmethod
import geopandas as gpd


class Stop(ABC):    
    def __init__(self, shapefile_path):
        self.gdf = gpd.read_file(shapefile_path)
        self._prepare_data()
    
    @abstractmethod
    def _prepare_data(self):
        pass
    
    @abstractmethod
    def visualize(self, ax=None):
        pass