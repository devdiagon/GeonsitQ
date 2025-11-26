import osmnx as ox
import folium
import geopandas as gpd
import pandas as pd

from settings import settings
from factories.district_layer_factory import DistrictLayerFactory
from factories.parks_layer_factory import ParksLayerFactory

class CityGraph:
    _instance = None
    _graph = None
    _districts = None
    _parks = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._districts = cls._load_districts()
            cls._graph = cls._load_graph()
            cls._parks = cls._load_parks()
        return cls._instance

    @classmethod
    def _load_graph(cls):
        gdfs = []

        for district in cls._districts:
            try:
                gdf_tmp = ox.geocode_to_gdf(district)
                gdfs.append(gdf_tmp)
            except Exception as e:
                print(f"No se pudo encontrar {district}: {e}")
        
        if gdfs:
            return gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
        return None
    
    @staticmethod
    def _load_districts():
        districts_names = []

        for district in settings.DISTRICTS:
            districts_names.append(f"{district}, {settings.CITY}, {settings.COUNTRY}")

        return districts_names
    
    @classmethod
    def _load_parks(cls):
        try:
            tags = {'leisure': 'park'}
            parks = ox.features_from_place(cls._districts, tags=tags)
            if parks is not None and len(parks) > 0:
                print(f"Se cargaron {len(parks)} parques.")
                return parks
            return None
        except Exception as e:
            print(f"Error cargando parques: {e}")
            return None
    
    def get_parks(self):
        return self._parks

    def get_graph(self):
        return self._graph
        
    def get_places(self):
        return self._districts

    def create_map(self, save_path : str):
        
        if self._graph is None or self._parks is None:
            print("No hay datos suficientes para crear el mapa")
            return None
        
        try:
            # Calcular el centro del mapa
            bounds = self._graph.total_bounds
            center_lat = (bounds[1] + bounds[3]) / 2
            center_lon = (bounds[0] + bounds[2]) / 2
            
            # Crear mapa base
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=12,
                tiles='OpenStreetMap'
            )
            
            # Crear capas usando factories concretas
            district_factory = DistrictLayerFactory()
            park_factory = ParksLayerFactory()
            

            district_layers = district_factory.create_layer(self)
            park_layers = park_factory.create_layer(self)

            # Añadir capas al mapa
            for layer in district_layers + park_layers:
                layer.add_to(m)
            
            # Añadir control de capas
            folium.LayerControl().add_to(m)
            
            # Guardar mapa
            if save_path:
                m.save(save_path)
                print(f"Mapa guardado en: {save_path}")
            
            return m
            
        except Exception as e:
            print(f"Error creando el mapa: {e}")
            return None