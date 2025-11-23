import osmnx as ox
import folium
import geopandas as gpd
import pandas as pd

from settings import settings

class CityGraph:
    _instance = None
    _graph = None
    _districts = None
    _pt_stops = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._districts = cls._load_parroquias()
            cls._graph = cls._load_graph()
            cls._pt_stops = cls._load_bus_stops()
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
    
    @classmethod
    def _load_bus_stops(cls):
        try:
            tags = {'public_transport': True}
            stops = ox.features_from_place(cls._districts, tags=tags)
            
            if stops is not None and len(stops) > 0:
                print(f"Se cargaron {len(stops)} paradas de bus.")
                return stops
            return None
        except Exception as e:
            print(f"Error cargando paradas de bus: {e}")
            return None

    @staticmethod
    def _load_parroquias():
        districts_names = []

        for district in settings.DISTRICTS:
            districts_names.append(f"{district}, {settings.CITY}, {settings.COUNTRY}")

        return districts_names

    def get_graph(self):
        return self._graph
    
    def get_bus_stops(self):
        return self._pt_stops
    
    def get_places(self):
        return self._districts

    def create_map(self, save_path):
        
        if self._graph is None or self._pt_stops is None:
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
            
            # Añadir límites de distritos en rojo
            for idx, row in self._graph.iterrows():
                if hasattr(row.geometry, '__geo_interface__'):
                    popup_text = f"<b>Distrito:</b> {row.get('display_name', 'N/A')}"
                    
                    folium.GeoJson(
                        row.geometry.__geo_interface__,
                        style_function=lambda x: {
                            'fillColor': 'red',
                            'color': 'red',
                            'weight': 2,
                            'fillOpacity': 0.1
                        },
                        popup=folium.Popup(popup_text, max_width=300)
                    ).add_to(m)
            
            # Añadir paradas de bus: Convertir a coordenadas y añadir marcadores
            for idx, stop in self._pt_stops.iterrows():
                if hasattr(stop.geometry, 'x') and hasattr(stop.geometry, 'y'):
                    lon, lat = stop.geometry.x, stop.geometry.y

                    # Obtener nombre de la parada si está disponible
                    popup_text = "Parada de bus"
                    if 'name' in stop and pd.notna(stop['name']):
                        popup_text = f"Parada: {stop['name']}"

                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=3,
                        popup=popup_text,
                        color='blue',
                        fillColor='blue',
                        fillOpacity=0.7,
                        weight=1
                    ).add_to(m)
            
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