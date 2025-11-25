from abstract.factory import RoadAxisFactory
from .bus_route import BusRoute
from .bus_stop import BusStop
from .bus_map import BusMap


class BusFactory(RoadAxisFactory):
    
    def __init__(self, shapefile_routes, shapefile_stops, route_code='Código_Ru'):
        self.shapefile_routes = shapefile_routes
        self.shapefile_stops = shapefile_stops
        self.route_code = route_code
    
    def create_route(self) -> BusRoute:
        return BusRoute(self.shapefile_routes, self.route_code)
    
    def create_stop(self) -> BusStop:
        return BusStop(self.shapefile_stops)
    
    def create_map(self) -> BusMap:
        routes = self.create_route()
        stops = self.create_stop()
        return BusMap(routes, stops)