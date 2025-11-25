from abstract.factory import RoadAxisFactory
from .metro_line import MetroLine
from .metro_station import MetroStation
from .metro_map import MetroMap


class MetroFactory(RoadAxisFactory):
    
    def __init__(self, shapefile_route, shapefile_stop):
        self.shapefile_route = shapefile_route
        self.shapefile_stop = shapefile_stop
    
    def create_route(self) -> MetroLine:
        return MetroLine(self.shapefile_route)
    
    def create_stop(self) -> MetroStation:
        return MetroStation(self.shapefile_stop)
    
    def create_map(self) -> MetroMap:
        route = self.create_route()
        stop = self.create_stop()
        return MetroMap(route, stop)