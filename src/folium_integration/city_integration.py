from .abstract.road_axis_factory import RoadAxisFactory


class CityTransportIntegration:
    
    def __init__(self):
        self.transport_systems = []
    
    def add_transport_system(self, factory: RoadAxisFactory):
        try:
            transport_map = factory.create_map()
            self.transport_systems.append(transport_map)
            print(f"✓ Sistema '{transport_map.system_name}' agregado")
        except Exception as e:
            print(f"Error agregando sistema de transporte: {e}")
    
    def add_layers_to_map(self, folium_map):
        print("\n=== Agregando capas de transporte al mapa ===")
        
        for transport_map in self.transport_systems:
            try:
                layers = transport_map.create_layers()
                for layer in layers:
                    layer.add_to(folium_map)
            except Exception as e:
                print(f"Error agregando capas de {transport_map.system_name}: {e}")
        
        return folium_map
    
    def get_all_bounds(self):
        """Obtiene los límites geográficos combinados de todos los sistemas"""
        import numpy as np
        
        min_lon, min_lat = float('inf'), float('inf')
        max_lon, max_lat = float('-inf'), float('-inf')
        
        for transport_map in self.transport_systems:
            try:
                # Obtener bounds de rutas
                route_gdf = transport_map.route.get_geodataframe()
                if route_gdf is not None and len(route_gdf) > 0:
                    bounds = route_gdf.total_bounds
                    if not np.any(np.isinf(bounds)) and not np.any(np.isnan(bounds)):
                        min_lon = min(min_lon, bounds[0])
                        min_lat = min(min_lat, bounds[1])
                        max_lon = max(max_lon, bounds[2])
                        max_lat = max(max_lat, bounds[3])
                
                # Obtener bounds de paradas
                stop_gdf = transport_map.stop.get_geodataframe()
                if stop_gdf is not None and len(stop_gdf) > 0:
                    bounds = stop_gdf.total_bounds
                    if not np.any(np.isinf(bounds)) and not np.any(np.isnan(bounds)):
                        min_lon = min(min_lon, bounds[0])
                        min_lat = min(min_lat, bounds[1])
                        max_lon = max(max_lon, bounds[2])
                        max_lat = max(max_lat, bounds[3])
                        
            except Exception as e:
                print(f"Error obteniendo bounds de {transport_map.system_name}: {e}")
        
        if np.isinf(min_lon) or np.isinf(min_lat):
            return None
        
        return [min_lon, min_lat, max_lon, max_lat]
    
    def get_center(self):
        """Calcula el centro geográfico de todos los sistemas de transporte"""
        bounds = self.get_all_bounds()
        
        if bounds is None:
            print(" No se pudieron calcular bounds, usando centro por defecto de Quito")
            return [-0.1807, -78.4678]
        
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        
        return [center_lat, center_lon]