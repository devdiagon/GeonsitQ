from ..abstract.road_axis_factory import RoadAxisFactory
from .metro_line import MetroLine
from .metro_station import MetroStation
from .metro_map import MetroMap


class MetroFactory(RoadAxisFactory):
    
    def __init__(self, route_shapefile, stop_shapefile, system_name="Metro"):
        self.route_shapefile = route_shapefile
        self.stop_shapefile = stop_shapefile
        self.system_name = system_name
    
    def create_route(self) -> MetroLine:
        return MetroLine(self.route_shapefile)
    
    def create_stop(self) -> MetroStation:
        return MetroStation(self.stop_shapefile)
    
    def create_map(self) -> MetroMap:
        route = self.create_route()
        stop = self.create_stop()
        return MetroMap(route, stop, self.system_name)