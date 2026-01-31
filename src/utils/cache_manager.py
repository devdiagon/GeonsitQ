import pickle
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Callable
import pandas as pd


class CacheManager:    
    def __init__(
        self,
        cache_dir: str = 'data/cache',
        ttl_hours: int = 24,
        version: str = '1.0.0'
    ):
        """        
        Args:
            cache_dir: Directorio para almacenar caché
            ttl_hours: Tiempo de vida del caché en horas
            version: Versión del formato de caché
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.version = version
        
        # Crear directorio si no existe
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_key(self, identifier: str, params: Optional[Dict] = None) -> str:
        """
        Genera una clave de caché única.
        
        Args:
            identifier: Identificador base
            params: Parámetros adicionales que afectan el caché
        
        Returns:
            str: Clave única
        """
        if params:
            params_str = json.dumps(params, sort_keys=True)
            combined = f"{identifier}_{params_str}"
        else:
            combined = identifier
        
        # Hash MD5
        hash_obj = hashlib.md5(combined.encode())
        return hash_obj.hexdigest()[:16]
    
    def _get_cache_path(self, key: str, extension: str = 'pkl') -> Path:
        filename = f"cache_{key}.{extension}"
        return self.cache_dir / filename
    
    def set(
        self,
        identifier: str,
        data: Any,
        params: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Guarda datos en caché.
        
        Args:
            identifier: Identificador del caché
            data: Datos a guardar
            params: Parámetros que afectan la clave
            metadata: Metadata adicional
        
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            key = self._generate_key(identifier, params)
            cache_path = self._get_cache_path(key)
            
            # Preparar estructura de caché
            cache_obj = {
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'version': self.version,
                'identifier': identifier,
                'params': params,
                'metadata': metadata or {}
            }
            
            # Guardar
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_obj, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            file_size = cache_path.stat().st_size / 1024
            print(f"Caché guardado: {cache_path.name} ({file_size:.1f} KB)")
            
            return True
            
        except Exception as e:
            print(f"Error guardando caché: {e}")
            return False
    
    def get(
        self,
        identifier: str,
        params: Optional[Dict] = None,
        validator: Optional[Callable] = None
    ) -> Optional[Any]:
        """
        Obtiene datos del caché.
        
        Args:
            identifier: Identificador del caché
            params: Parámetros que afectan la clave
            validator: Función opcional para validar los datos
        
        Returns:
            Datos del caché o None si no existe/expiró/inválido
        """
        try:
            key = self._generate_key(identifier, params)
            cache_path = self._get_cache_path(key)
            
            if not cache_path.exists():
                return None
            
            # Cargar caché
            with open(cache_path, 'rb') as f:
                cache_obj = pickle.load(f)
            
            # Validar versión
            if cache_obj.get('version') != self.version:
                print(f"Versión de caché incompatible")
                cache_path.unlink()
                return None
            
            # Validar TTL
            timestamp = datetime.fromisoformat(cache_obj['timestamp'])
            age = datetime.now() - timestamp
            
            if age > timedelta(hours=self.ttl_hours):
                print(f"Caché expirado ({age.total_seconds()/3600:.1f}h)")
                cache_path.unlink()
                return None
            
            # Validar datos si se proporciona validador
            data = cache_obj['data']
            if validator and not validator(data):
                print(f"Validación de caché falló")
                cache_path.unlink()
                return None
            
            print(f"Caché válido: {cache_path.name} (edad: {age.total_seconds()/3600:.1f}h)")
            return data
            
        except Exception as e:
            print(f"Error leyendo caché: {e}")
            # Limpiar caché corrupto
            try:
                cache_path.unlink()
            except:
                pass
            return None
    
    def invalidate(self, identifier: str, params: Optional[Dict] = None) -> bool:
        """
        Invalida un caché específico.
        
        Args:
            identifier: Identificador del caché
            params: Parámetros que afectan la clave
        
        Returns:
            bool: True si se invalidó
        """
        try:
            key = self._generate_key(identifier, params)
            cache_path = self._get_cache_path(key)
            
            if cache_path.exists():
                cache_path.unlink()
                print(f"🗑️  Caché invalidado: {cache_path.name}")
                return True
            else:
                print(f"No existe caché para invalidar")
                return False
                
        except Exception as e:
            print(f"Error invalidando caché: {e}")
            return False
    
    def clear_all(self) -> int:
        try:
            cache_files = list(self.cache_dir.glob('cache_*.pkl'))
            count = 0
            
            for cache_file in cache_files:
                try:
                    cache_file.unlink()
                    count += 1
                except:
                    pass
            
            if count > 0:
                print(f"{count} caché(s) eliminado(s)")
            
            return count
            
        except Exception as e:
            print(f"Error limpiando cachés: {e}")
            return 0
    
    def cleanup_expired(self) -> int:
        try:
            cache_files = list(self.cache_dir.glob('cache_*.pkl'))
            count = 0
            
            for cache_file in cache_files:
                try:
                    # Verificar edad
                    mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                    age = datetime.now() - mtime
                    
                    if age > timedelta(hours=self.ttl_hours):
                        cache_file.unlink()
                        count += 1
                except:
                    pass
            
            if count > 0:
                print(f"{count} caché(s) expirado(s) eliminado(s)")
            
            return count
            
        except Exception as e:
            print(f"Error limpiando cachés expirados: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del caché.
        
        Returns:
            Dict con estadísticas
        """
        try:
            cache_files = list(self.cache_dir.glob('cache_*.pkl'))
            
            total_size = 0
            valid_count = 0
            expired_count = 0
            
            for cache_file in cache_files:
                try:
                    stat = cache_file.stat()
                    total_size += stat.st_size
                    
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    age = datetime.now() - mtime
                    
                    if age <= timedelta(hours=self.ttl_hours):
                        valid_count += 1
                    else:
                        expired_count += 1
                except:
                    pass
            
            return {
                'total_files': len(cache_files),
                'valid_files': valid_count,
                'expired_files': expired_count,
                'total_size_mb': total_size / (1024 * 1024),
                'cache_dir': str(self.cache_dir),
                'ttl_hours': self.ttl_hours
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {}