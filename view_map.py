import os
from mapq import CityGraph

def create_city_map(save_path):    
    city = CityGraph()
    city2 = CityGraph()
    print(f"city y city2 misma instancia: {city is city2}")
    return city.create_map(save_path)

if __name__ == "__main__":
    map_dir = "maps"

    if not os.path.exists(map_dir):
        os.makedirs(map_dir)
    
    mapa = create_city_map(
        save_path=f"{map_dir}/city_map.html"
    )
    
    if mapa:
        print("Mapa creado exitosamente!")
    else:
        print("Error al crear el mapa")