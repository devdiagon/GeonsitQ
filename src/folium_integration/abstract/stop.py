from abc import ABC, abstractmethod
import geopandas as gpd


class Stop(ABC):
    
    def __init__(self, shapefile_path):
        self.shapefile_path = shapefile_path
        self.gdf = None
        self.prepare_data()
    
    @abstractmethod
    def prepare_data(self):
        pass
    
    @abstractmethod
    def add_to_map(self, feature_group):
        pass
    
    def get_geodataframe(self):
        return self.gdf