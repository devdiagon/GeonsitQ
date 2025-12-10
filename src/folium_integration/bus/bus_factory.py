from ..abstract.road_axis_factory import RoadAxisFactory
from .bus_route import BusRoute
from .bus_stop import BusStop
from .bus_map import BusMap


class BusFactory(RoadAxisFactory):
    
    def __init__(self, route_shapefile, stop_shapefile, system_name="Buses", max_routes=50, max_stops=1000):
        self.route_shapefile = route_shapefile
        self.stop_shapefile = stop_shapefile
        self.system_name = system_name
        self.max_routes = max_routes
        self.max_stops = max_stops
    
    def create_route(self) -> BusRoute:
        return BusRoute(self.route_shapefile, self.max_routes)
    
    def create_stop(self) -> BusStop:
        return BusStop(self.stop_shapefile, self.max_stops)
    
    def create_map(self) -> BusMap:
        route = self.create_route()
        stop = self.create_stop()
        return BusMap(route, stop, self.system_name)