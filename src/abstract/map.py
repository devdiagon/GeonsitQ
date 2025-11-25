from abc import ABC, abstractmethod


class Map(ABC):    
    def __init__(self, route, stop):
        self.route = route
        self.stop = stop
    
    @abstractmethod
    def visualize(self, ax=None, mostrar_nombres=False):
        pass