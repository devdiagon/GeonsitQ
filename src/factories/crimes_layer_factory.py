import folium
from .map_layer_factory import MapLayerFactory
from .adapters.crimes_adapter import CrimesAdapter

class CrimesLayerFactory(MapLayerFactory):
    
    def __init__(self, shapefile_path=None, layer_type='colored_polygons', intensity_field=None, color_field='color'):
        self.shapefile_path = shapefile_path
        self.layer_type = layer_type
        self.intensity_field = intensity_field
        self.color_field = color_field
    
    def create_layer(self, citygraph=None):
        layers = []
        
        try:
            print(f"Creando capa de Delitos desde shapefile...")
            
            # Usar el Adapter para cargar el shapefile
            adapter = CrimesAdapter(
                self.shapefile_path,
                intensity_field=self.intensity_field,
                color_field=self.color_field
            )
            
            # Crear la visualización según el tipo
            if self.layer_type == 'colored_polygons':
                # Polígonos coloreados
                geojson = adapter.to_folium_colored_polygons()
                if geojson:
                    feature_group = folium.FeatureGroup(
                        name='Zonas por Categoría',
                        show=True
                    )
                    geojson.add_to(feature_group)
                    layers.append(feature_group)
            
            if layers:
                print(f"✓ Capa de Delitos creada ({self.layer_type})")
            else:
                print("No se pudo crear la capa de  Delitos")
                
        except Exception as e:
            print(f"Error creando capa Delitos: {e}")
            import traceback
            traceback.print_exc()
        
        return layers