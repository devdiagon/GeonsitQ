import os
from mapq import CityGraph

def crear_mapa_completo():
    print("\n=== CREANDO MAPA INTEGRADO ===\n")

    city = CityGraph()
    
    # Crear mapa con todos los sistemas
    mapa = city.create_map(
        save_path=f"{map_dir}/city_map_complete.html",
        include_transport=True,
        include_metro=True,
        include_buses=True,
        include_crimes=True,
        heatmap_type='colored_polygons',
        max_rutas=204
    )
    
    if mapa:
        print("\n✓ Mapa creado exitosamente")


if __name__ == "__main__":
    map_dir = "maps"

    if not os.path.exists(map_dir):
        os.makedirs(map_dir)

    crear_mapa_completo()