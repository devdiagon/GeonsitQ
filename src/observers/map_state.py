from typing import Set, List, Optional, Dict, Any
from abc import ABC, abstractmethod
from strategies.base_strategy import BaseStrategy


class Observer(ABC):    
    @abstractmethod
    def update(self, state: 'MapState', change_type: str, **kwargs):
        """
        Método llamado cuando el estado cambia.
        
        Args:
            state: Instancia de MapState que cambió
            change_type: Tipo de cambio ('strategy', 'layers', 'viewport', etc.)
            **kwargs: Datos adicionales sobre el cambio
        """
        pass


class MapState:
    """
    Estado observable del mapa.
    
    Mantiene:
    - Estrategia de análisis actual
    - Capas activas/visibles
    - Área visible del mapa (viewport)
    - Otros parámetros de configuración
    
    Notifica a los observadores cuando cualquiera de estos cambia.
    """
    
    def __init__(self):
        # Estado interno
        self._current_strategy: Optional[BaseStrategy] = None
        self._active_layers: Set[str] = set()
        self._viewport_bounds: Optional[Dict[str, float]] = None
        self._additional_params: Dict[str, Any] = {}
        
        # Lista de observadores
        self._observers: List[Observer] = []
        
        # Flag para habilitar/deshabilitar notificaciones
        self._notifications_enabled: bool = True
    
    # ========== Gestión de Observadores ==========
    
    def attach(self, observer: Observer):
        """
        Registra un observador.
        
        Args:
            observer: Instancia de Observer a registrar
        """
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"Observer registrado: {observer.__class__.__name__}")
        else:
            print(f" Observer ya registrado: {observer.__class__.__name__}")
    
    def detach(self, observer: Observer):
        """
        Desregistra un observador.
        
        Args:
            observer: Instancia de Observer a desregistrar
        """
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"Observer desuscrito: {observer.__class__.__name__}")
        else:
            print(f" Observer no estaba registrado: {observer.__class__.__name__}")
    
    def notify(self, change_type: str, **kwargs):
        """
        Notifica a todos los observadores sobre un cambio.
        
        Args:
            change_type: Tipo de cambio que ocurrió
            **kwargs: Datos adicionales sobre el cambio
        """
        if not self._notifications_enabled:
            return
        
        print(f"\nNotificando cambio: {change_type}")
        print(f"   Observadores a notificar: {len(self._observers)}")
        
        for observer in self._observers:
            try:
                observer.update(self, change_type, **kwargs)
            except Exception as e:
                print(f"Error en observer {observer.__class__.__name__}: {e}")
    
    def disable_notifications(self):
        self._notifications_enabled = False
        print("Notificaciones deshabilitadas")
    
    def enable_notifications(self):
        self._notifications_enabled = True
        print("Notificaciones habilitadas")
    
    # ========== Getters y Setters con Notificación ==========
    
    @property
    def current_strategy(self) -> Optional[BaseStrategy]:
        return self._current_strategy
    
    def set_strategy(self, strategy: BaseStrategy):
        """
        Establece una nueva estrategia y notifica.
        
        Args:
            strategy: Nueva estrategia a aplicar
        """
        old_strategy = self._current_strategy
        self._current_strategy = strategy
        
        print(f"\nEstrategia cambiada:")
        print(f"   Anterior: {old_strategy.get_name() if old_strategy else 'Ninguna'}")
        print(f"   Nueva: {strategy.get_name()}")
        
        self.notify(
            'strategy',
            old_strategy=old_strategy,
            new_strategy=strategy
        )
    
    @property
    def active_layers(self) -> Set[str]:
        return self._active_layers.copy()
    
    def set_active_layers(self, layers: Set[str]):
        """
        Establece las capas activas y notifica.
        
        Args:
            layers: Conjunto de nombres de capas activas
        """
        old_layers = self._active_layers.copy()
        self._active_layers = layers.copy()
        
        added = layers - old_layers
        removed = old_layers - layers
        
        if added or removed:
            print(f"\n Capas modificadas:")
            if added:
                print(f"   Agregadas: {', '.join(added)}")
            if removed:
                print(f"   Removidas: {', '.join(removed)}")
            
            self.notify(
                'layers',
                old_layers=old_layers,
                new_layers=layers,
                added=added,
                removed=removed
            )
    
    def toggle_layer(self, layer_name: str):
        """
        Activa/desactiva una capa individual.
        
        Args:
            layer_name: Nombre de la capa a togglear
        """
        if layer_name in self._active_layers:
            self._active_layers.remove(layer_name)
            action = "desactivada"
        else:
            self._active_layers.add(layer_name)
            action = "activada"
        
        print(f"\nCapa '{layer_name}' {action}")
        
        self.notify(
            'layer_toggle',
            layer_name=layer_name,
            is_active=(layer_name in self._active_layers)
        )
    
    @property
    def viewport_bounds(self) -> Optional[Dict[str, float]]:
        return self._viewport_bounds.copy() if self._viewport_bounds else None
    
    def set_viewport_bounds(self, bounds: Dict[str, float]):
        """
        Establece los límites del viewport y notifica.
        
        Args:
            bounds: Dict con 'north', 'south', 'east', 'west'
        """
        old_bounds = self._viewport_bounds
        self._viewport_bounds = bounds.copy()
        
        # Solo notificar si cambió significativamente
        if self._bounds_changed_significantly(old_bounds, bounds):
            print(f"\n Viewport cambió:")
            print(f"   Bounds: {bounds}")
            
            self.notify(
                'viewport',
                old_bounds=old_bounds,
                new_bounds=bounds
            )
    
    def _bounds_changed_significantly(
        self,
        old_bounds: Optional[Dict],
        new_bounds: Dict,
        threshold: float = 0.01
    ) -> bool:
        """
        Verifica si el cambio de bounds es significativo.
        
        Evita notificaciones por cambios mínimos (zoom/pan pequeños).
        """
        if old_bounds is None:
            return True
        
        # Calcular diferencia en cada dirección
        for key in ['north', 'south', 'east', 'west']:
            if abs(old_bounds.get(key, 0) - new_bounds.get(key, 0)) > threshold:
                return True
        
        return False
    
    def set_param(self, key: str, value: Any):
        """
        Establece un parámetro adicional.
        
        Args:
            key: Nombre del parámetro
            value: Valor del parámetro
        """
        old_value = self._additional_params.get(key)
        self._additional_params[key] = value
        
        if old_value != value:
            print(f"\n Parámetro '{key}' cambiado: {old_value} → {value}")
            
            self.notify(
                'param',
                param_name=key,
                old_value=old_value,
                new_value=value
            )
    
    def get_param(self, key: str, default: Any = None) -> Any:
        return self._additional_params.get(key, default)
    
    # ========== Utilidades ==========
    
    def get_state_summary(self) -> Dict[str, Any]:
        return {
            'strategy': self._current_strategy.get_name() if self._current_strategy else None,
            'active_layers': list(self._active_layers),
            'viewport_bounds': self._viewport_bounds,
            'num_observers': len(self._observers),
            'notifications_enabled': self._notifications_enabled,
            'additional_params': self._additional_params.copy()
        }
    
    def reset(self):        
        self._current_strategy = None
        self._active_layers.clear()
        self._viewport_bounds = None
        self._additional_params.clear()
        
        self.notify('reset')
    
    def __repr__(self) -> str:
        strategy_name = self._current_strategy.get_name() if self._current_strategy else 'None'
        return (
            f"MapState("
            f"strategy='{strategy_name}', "
            f"layers={len(self._active_layers)}, "
            f"observers={len(self._observers)}"
            f")"
        )