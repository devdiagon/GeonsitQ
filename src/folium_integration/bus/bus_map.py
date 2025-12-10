import folium
from ..abstract.map import Map


class BusMap(Map):
    
    def create_layers(self):
        layers = []
        
        try:
            rutas_group = folium.FeatureGroup(
                name=f'🚌 {self.system_name} - Rutas',
                show=True
            )
            self.route.add_to_map(rutas_group)
            layers.append(rutas_group)
            
            paradas_group = folium.FeatureGroup(
                name=f'🚏 {self.system_name} - Paradas',
                show=True
            )
            self.stop.add_to_map(paradas_group)
            layers.append(paradas_group)
            
            print(f"✓ Mapa de Buses creado exitosamente")
            
        except Exception as e:
            print(f"Error creando mapa de Buses: {e}")
        
        return layers
    
    def get_layer_name(self):
        return self.system_name