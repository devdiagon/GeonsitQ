import folium
from ..abstract.map import Map


class MetroMap(Map):
    
    def create_layers(self):
        layers = []
        
        try:
            # Crear grupo de características para Metro
            metro_group = folium.FeatureGroup(
                name=self.get_layer_name(),
                show=True
            )
            
            # Agregar rutas y estaciones
            self.route.add_to_map(metro_group)
            self.stop.add_to_map(metro_group)
            
            layers.append(metro_group)
            
            print(f"✓ Mapa de Metro creado exitosamente")
            
        except Exception as e:
            print(f"Error creando mapa de Metro: {e}")
        
        return layers
    
    def get_layer_name(self):
        return f' {self.system_name}'