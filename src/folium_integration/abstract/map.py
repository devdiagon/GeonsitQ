from abc import ABC, abstractmethod

class Map(ABC):
    
    def __init__(self, route, stop, system_name):
        self.route = route
        self.stop = stop
        self.system_name = system_name
    
    @abstractmethod
    def create_layers(self):
        pass
    
    @abstractmethod
    def get_layer_name(self):
        pass