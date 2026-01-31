from observers.map_state import Observer, MapState
from analyzers.district_analyzer import DistrictAnalyzer


class CacheObserver(Observer):    
    def __init__(self, district_analyzer: DistrictAnalyzer):
        self.analyzer = district_analyzer
        self.cache_valid = True
    
    def update(self, state: MapState, change_type: str, **kwargs):
        """
        Maneja cambios de estado.
        
        Args:
            state: Estado del mapa
            change_type: Tipo de cambio
            **kwargs: Datos adicionales del cambio
        """
        # Cambios que invalidan caché
        invalidating_changes = [
            'layers',
            'param', 
            'reset'  
        ]
        
        if change_type in invalidating_changes:
            self._invalidate_cache(change_type, **kwargs)
    
    def _invalidate_cache(self, reason: str, **kwargs):
        """
        Invalida el caché de métricas.
        
        Args:
            reason: Razón de la invalidación
            **kwargs: Datos adicionales
        """
        # Verificar si el cambio realmente afecta los datos base
        if reason == 'layers':
            # Solo invalidar si cambiaron capas que afectan métricas
            # (criminalidad, transporte, parques, servicios)
            affected_layers = {'crimes', 'bus_routes', 'bus_stops', 'metro', 'parks', 'services'}
            
            added = kwargs.get('added', set())
            removed = kwargs.get('removed', set())
            
            if not (added & affected_layers or removed & affected_layers):
                # Cambio en capas visuales, no afecta métricas
                print(" CacheObserver: Cambio en capas visuales, caché sigue válido")
                return
        
        print(f"\n CacheObserver: Invalidando caché")
        print(f"   Razón: {reason}")
        
        # Invalidar caché del analyzer
        self.analyzer.invalidate_cache()
        self.cache_valid = False
        
        print("Caché invalidado - se recalculará en próxima solicitud")
    
    def is_cache_valid(self) -> bool:
        return self.cache_valid
    
    def mark_cache_valid(self):
        self.cache_valid = True
        print("CacheObserver: Caché marcado como válido")