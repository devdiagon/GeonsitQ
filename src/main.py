from metro.metro_factory import MetroFactory
from bus.bus_factory import BusFactory
from settings import settings

def main():
    # Rutas de los shapefiles
    SHP_METRO = 'D:/rutas/data/temp/eje_metro_l/eje_metro_l.shp'
    SHP_METRO_STATIONS = 'D:/rutas/data/temp/estacion_metro_a/estacion_metro_a.shp'
    SHP_BUS_ROUTES = 'D:/rutas/data/Rutas_urbanas_convencionales/7.Rutas Urbanas Convencionales/Rutas_urbanas_convencionales.shp'
    SHP_BUS_STOPS = 'D:/rutas/data/Paradas_DMQ/11.Paradas buses DMQ/Paradas_Buses_DMQ.shp'

    # ========== Crear sistema Metro ==========
    print("Creando sistema Metro...")
    metro_factory = MetroFactory(SHP_METRO, SHP_METRO_STATIONS)
    metro_map = metro_factory.create_map()
    
    metro_map.visualize(show_names=True, title="Sistema Metro")

    # ========== Crear sistema Buses ==========
    print("\nCreando sistema de Buses...")
    bus_factory = BusFactory(SHP_BUS_ROUTES, SHP_BUS_STOPS, route_code='Código_Ru')
    bus_map = bus_factory.create_map()
    
    bus_map.visualize(title="Sistema de Buses Urbanos")


if __name__ == "__main__":
    main()