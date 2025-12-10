from metro.metro_factory import MetroFactory
from bus.bus_factory import BusFactory
from settings import settings

def main():
    # ========== Crear sistema Metro ==========
    print("Creando sistema Metro...")
    metro_factory = MetroFactory(settings.SHP_METRO, settings.SHP_METRO_STATIONS)
    metro_map = metro_factory.create_map()
    
    metro_map.visualize(show_names=True, title="Sistema Metro")

    # ========== Crear sistema Buses ==========
    print("\nCreando sistema de Buses...")
    bus_factory = BusFactory(settings.SHP_BUS_ROUTES, settings.SHP_BUS_STOPS, route_code='Código_Ru')
    bus_map = bus_factory.create_map()
    
    bus_map.visualize(title="Sistema de Buses Urbanos")


if __name__ == "__main__":
    main()