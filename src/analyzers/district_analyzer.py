"""
Analizador principal de distritos.
Coordina el cálculo de todas las métricas y gestiona la caché.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import yaml
import hashlib
import json

# Imports de módulos propios
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from analyzers.metrics_calculator import (
    calculate_safety_score,
    calculate_transport_score,
    calculate_green_score,
    calculate_services_score
)
from analyzers.normalizer import (
    normalize_min_max,
    handle_missing_values,
    safe_normalize
)
from settings import settings


class DistrictAnalyzer:
    """
    Clase principal para análisis de distritos.
    
    Responsabilidades:
    - Cargar datos de distritos y capas relacionadas
    - Calcular métricas por distrito
    - Gestionar caché de resultados
    - Proporcionar DataFrame con todas las métricas
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Inicializa el analizador.
        
        Args:
            config_path: Ruta al archivo de configuración YAML
        """
        self.config = self._load_config(config_path)
        self.cache_dir = Path(self.config.get('cache', {}).get('directory', 'data/cache'))
        self.cache_file = self.cache_dir / self.config.get('cache', {}).get('metrics_file', 'district_metrics.pkl')
        self.cache_ttl_hours = self.config.get('cache', {}).get('ttl_hours', 24)
        
        # DataFrames de datos
        self.districts_gdf = None
        self.crime_gdf = None
        self.bus_stops_gdf = None
        self.bus_routes_gdf = None
        self.metro_stations_gdf = None
        self.metro_line_gdf = None
        self.parks_gdf = None
        self.tourist_places_gdf = None
        
        # DataFrame de métricas calculadas
        self.metrics_df = None
        
    def _load_config(self, config_path: str) -> dict:
        """Carga configuración desde YAML."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error cargando config: {e}. Usando configuración por defecto.")
            return self._default_config()
    
    def _default_config(self) -> dict:
        """Configuración por defecto si no se puede cargar el archivo."""
        return {
            'cache': {
                'enabled': True,
                'directory': 'data/cache',
                'metrics_file': 'district_metrics.pkl',
                'ttl_hours': 24
            },
            'normalization': {
                'method': 'min_max',
                'handle_nulls': 'neutral',
                'safety_inversion': True
            },
            'analysis': {
                'transport': {
                    'max_distance_to_metro': 500
                },
                'green': {
                    'min_park_area': 1000,
                    'ideal_green_coverage': 0.15
                }
            }
        }
    
    def load_data(
        self,
        districts_gdf: gpd.GeoDataFrame,
        parks_gdf: Optional[gpd.GeoDataFrame] = None,
        tourist_places_gdf: Optional[gpd.GeoDataFrame] = None
    ):
        """
        Carga datos necesarios para el análisis.
        
        Args:
            districts_gdf: GeoDataFrame con distritos (obligatorio)
            parks_gdf: GeoDataFrame con parques (opcional)
            tourist_places_gdf: GeoDataFrame con lugares turísticos (opcional)
        """
        print("\nCargando datos para análisis...")
        
        # Distritos (obligatorio)
        if districts_gdf is None or len(districts_gdf) == 0:
            raise ValueError("Se requiere districts_gdf con al menos un distrito")
        
        self.districts_gdf = districts_gdf
        print(f"Distritos cargados: {len(self.districts_gdf)}")
        
        # Parques (opcional)
        if parks_gdf is not None and len(parks_gdf) > 0:
            self.parks_gdf = parks_gdf
            print(f"Parques cargados: {len(self.parks_gdf)}")
        else:
            print(" No se cargaron parques")
        
        # Lugares turísticos (opcional)
        if tourist_places_gdf is not None and len(tourist_places_gdf) > 0:
            self.tourist_places_gdf = tourist_places_gdf
            print(f"Lugares turísticos cargados: {len(self.tourist_places_gdf)}")
        else:
            print(" No se cargaron lugares turísticos")
        
        # Cargar shapefiles
        self._load_shapefiles()
    
    def _load_shapefiles(self):
        """Carga shapefiles desde settings."""
        print("\nCargando shapefiles...")
        
        # Criminalidad
        try:
            self.crime_gdf = gpd.read_file(settings.SHP_CRIMES)
            if self.crime_gdf.crs != 'EPSG:4326':
                self.crime_gdf = self.crime_gdf.to_crs('EPSG:4326')
            print(f"Zonas de criminalidad: {len(self.crime_gdf)}")
        except Exception as e:
            print(f" Error cargando crímenes: {e}")
        
        # Paradas de bus
        try:
            self.bus_stops_gdf = gpd.read_file(settings.SHP_BUS_STOPS)
            if self.bus_stops_gdf.crs != 'EPSG:4326':
                self.bus_stops_gdf = self.bus_stops_gdf.to_crs('EPSG:4326')
            print(f"Paradas de bus: {len(self.bus_stops_gdf)}")
        except Exception as e:
            print(f" Error cargando paradas de bus: {e}")
        
        # Rutas de bus
        try:
            self.bus_routes_gdf = gpd.read_file(settings.SHP_BUS_ROUTES)
            if self.bus_routes_gdf.crs != 'EPSG:4326':
                self.bus_routes_gdf = self.bus_routes_gdf.to_crs('EPSG:4326')
            print(f"Rutas de bus: {len(self.bus_routes_gdf)}")
        except Exception as e:
            print(f" Error cargando rutas de bus: {e}")
        
        # Estaciones de metro
        try:
            self.metro_stations_gdf = gpd.read_file(settings.SHP_METRO_STATIONS)
            if self.metro_stations_gdf.crs != 'EPSG:4326':
                self.metro_stations_gdf = self.metro_stations_gdf.to_crs('EPSG:4326')
            print(f"Estaciones de metro: {len(self.metro_stations_gdf)}")
        except Exception as e:
            print(f" Error cargando estaciones de metro: {e}")
        
        # Línea de metro
        try:
            self.metro_line_gdf = gpd.read_file(settings.SHP_METRO)
            if self.metro_line_gdf.crs != 'EPSG:4326':
                self.metro_line_gdf = self.metro_line_gdf.to_crs('EPSG:4326')
            print(f"Línea de metro: {len(self.metro_line_gdf)}")
        except Exception as e:
            print(f" Error cargando línea de metro: {e}")
    
    def analyze_all_districts(self, force_refresh: bool = False) -> pd.DataFrame:
        """
        Analiza todos los distritos y calcula métricas.
        
        Args:
            force_refresh: Si True, ignora caché y recalcula todo
        
        Returns:
            DataFrame con todas las métricas por distrito
        """
        # Intentar cargar desde caché
        if not force_refresh and self.config.get('cache', {}).get('enabled', True):
            cached_metrics = self.get_cached_metrics()
            if cached_metrics is not None:
                print("Métricas cargadas desde caché")
                self.metrics_df = cached_metrics
                return self.metrics_df
        
        print("\nCalculando métricas para todos los distritos...")
        
        if self.districts_gdf is None:
            raise ValueError("No se han cargado distritos. Usa load_data() primero.")
        
        # Lista para almacenar resultados
        results = []
        
        # Iterar sobre cada distrito
        for idx, district in self.districts_gdf.iterrows():
            district_metrics = self._analyze_single_district(district, idx)
            results.append(district_metrics)
        
        # Crear DataFrame
        self.metrics_df = pd.DataFrame(results)
        
        # Guardar en caché
        if self.config.get('cache', {}).get('enabled', True):
            self._save_to_cache(self.metrics_df)
        
        print(f"\nAnálisis completado: {len(self.metrics_df)} distritos")
        
        return self.metrics_df
    
    def _analyze_single_district(self, district: gpd.GeoSeries, district_idx: int) -> dict:
        """
        Analiza un distrito individual y calcula todas sus métricas.
        
        Args:
            district: Serie con datos del distrito
            district_idx: Índice del distrito
        
        Returns:
            Dict con todas las métricas del distrito
        """
        district_polygon = district.geometry
        
        # Obtener nombre del distrito
        district_name = district.get('display_name', district.get('name', f'Distrito_{district_idx}'))
        
        print(f" Analizando: {district_name}")
        
        metrics = {
            'district_id': district_idx,
            'district_name': district_name,
            'geometry': district_polygon
        }
        
        # Calcular Safety Score
        if self.crime_gdf is not None:
            safety = calculate_safety_score(
                district_polygon,
                self.crime_gdf,
                gridcode_field='gridcode',
                invert_scale=self.config.get('normalization', {}).get('safety_inversion', True)
            )
            metrics['safety'] = safety
        else:
            metrics['safety'] = 0.5  # Neutral
        
        # Calcular Transport Score
        transport = calculate_transport_score(
            district_polygon,
            bus_stops_gdf=self.bus_stops_gdf,
            bus_routes_gdf=self.bus_routes_gdf,
            metro_stations_gdf=self.metro_stations_gdf,
            metro_line_gdf=self.metro_line_gdf,
            route_id_field='Código_Ru'
        )
        metrics['transport'] = transport
        
        # Calcular Green Score
        if self.parks_gdf is not None:
            green_config = self.config.get('analysis', {}).get('green', {})
            green = calculate_green_score(
                district_polygon,
                self.parks_gdf,
                ideal_coverage=green_config.get('ideal_green_coverage', 0.15),
                min_park_area=green_config.get('min_park_area', 1000.0)
            )
            metrics['green'] = green
        else:
            metrics['green'] = 0.0
        
        # Calcular Services Score
        if self.tourist_places_gdf is not None:
            services = calculate_services_score(
                district_polygon,
                tourist_places_gdf=self.tourist_places_gdf
            )
            metrics['services'] = services
        else:
            metrics['services'] = 0.0
        
        return metrics
    
    # =================== CACHE RELATED METHODS ===================

    def _generate_cache_key(self) -> str:
        cache_config = {
            'safety_inversion': self.config.get('normalization', {}).get('safety_inversion', True),
            'ideal_green_coverage': self.config.get('analysis', {}).get('green', {}).get('ideal_green_coverage', 0.15),
            'min_park_area': self.config.get('analysis', {}).get('green', {}).get('min_park_area', 1000.0),
        }
        
        config_str = json.dumps(cache_config, sort_keys=True)
        cache_key = hashlib.md5(config_str.encode()).hexdigest()[:8]
        
        return cache_key
    
    def _get_cache_filepath(self) -> Path:
        cache_key = self._generate_cache_key()
        filename = f"district_metrics_{cache_key}.pkl"
        return self.cache_dir / filename

    def get_cache_info(self) -> Dict[str, any]:
        """
        Obtiene información sobre el estado del caché.
        
        Returns:
            Dict con información del caché
        """
        cache_file = self._get_cache_filepath()
        
        info = {
            'cache_file': cache_file.name,
            'exists': cache_file.exists(),
            'enabled': self.config.get('cache', {}).get('enabled', True),
            'ttl_hours': self.cache_ttl_hours,
            'config_hash': self._generate_cache_key()
        }
        
        if cache_file.exists():
            try:
                stat = cache_file.stat()
                cache_time = datetime.fromtimestamp(stat.st_mtime)
                age = datetime.now() - cache_time
                
                info.update({
                    'size_kb': stat.st_size / 1024,
                    'created': cache_time.isoformat(),
                    'age_hours': age.total_seconds() / 3600,
                    'is_valid': age <= timedelta(hours=self.cache_ttl_hours)
                })
                
                # Intentar leer metadata
                try:
                    with open(cache_file, 'rb') as f:
                        cached_data = pickle.load(f)
                    
                    if isinstance(cached_data, dict) and 'metadata' in cached_data:
                        info['metadata'] = cached_data['metadata']
                except:
                    pass
                    
            except Exception as e:
                info['error'] = str(e)
        
        return info

    def get_cached_metrics(self) -> Optional[pd.DataFrame]:
        """
        Intenta cargar métricas desde caché.
        
        Returns:
            DataFrame con métricas o None si no hay caché válido
        """
        cache_file = self._get_cache_filepath()

        if not cache_file.exists():
            print(f" No existe archivo de caché: {cache_file.name}")
            return None
        
        try:
            # Cargar caché
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Validar estructura del caché
            if not isinstance(cached_data, dict):
                print(" Formato de caché inválido (no es dict)")
                return None
            
            required_keys = ['metrics_df', 'timestamp', 'config_hash', 'version']
            if not all(key in cached_data for key in required_keys):
                print(" Caché incompleto, faltan claves requeridas")
                return None
            
            # Verificar versión del caché
            cache_version = cached_data.get('version', '1.0.0')
            current_version = '1.0.0'
            
            if cache_version != current_version:
                print(f" Versión de caché incompatible: {cache_version} vs {current_version}")
                return None
            
            # Verificar hash de configuración
            cached_hash = cached_data.get('config_hash')
            current_hash = self._generate_cache_key()
            
            if cached_hash != current_hash:
                print(f" Configuración cambió desde caché (hash: {cached_hash} vs {current_hash})")
                return None
            
            # Verificar antigüedad (TTL)
            cache_timestamp = cached_data.get('timestamp')
            cache_time = datetime.fromisoformat(cache_timestamp)
            age = datetime.now() - cache_time
            
            if age > timedelta(hours=self.cache_ttl_hours):
                print(f" Caché expirado (edad: {age.total_seconds()/3600:.1f} horas > {self.cache_ttl_hours} horas)")
                return None
            
            # Caché válido
            metrics_df = cached_data['metrics_df']
            
            # Validar que tiene las columnas esperadas
            required_cols = ['district_name', 'safety', 'transport', 'green', 'services']
            if not all(col in metrics_df.columns for col in required_cols):
                print(" Caché con columnas faltantes")
                return None
            
            print(f"Caché válido encontrado:")
            print(f"   Archivo: {cache_file.name}")
            print(f"   Edad: {age.total_seconds()/3600:.1f} horas")
            print(f"   Distritos: {len(metrics_df)}")
            
            return metrics_df
            
        except Exception as e:
            print(f" Error cargando caché: {e}")
            try:
                cache_file.unlink()
                print(" Caché corrupto eliminado")
            except:
                pass
            return None
    
    def _save_to_cache(self, metrics_df: pd.DataFrame):
        """Guarda métricas en caché."""
        try:
            # Asegurar que el directorio existe
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # Preparar datos para caché
            cache_data = {
                'metrics_df': metrics_df,
                'timestamp': datetime.now().isoformat(),
                'config_hash': self._generate_cache_key(),
                'version': '1.0.0',
                'metadata': {
                    'num_districts': len(metrics_df),
                    'columns': list(metrics_df.columns),
                    'config': {
                        'ttl_hours': self.cache_ttl_hours,
                        'safety_inversion': self.config.get('normalization', {}).get('safety_inversion', True),
                    }
                }
            }

            # Guardar en archivo
            cache_file = self._get_cache_filepath()
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Obtener tamaño del archivo
            file_size = cache_file.stat().st_size / 1024  # KB
            
            print(f"Métricas guardadas en caché:")
            print(f"   Archivo: {cache_file.name}")
            print(f"   Tamaño: {file_size:.1f} KB")
            print(f"   Distritos: {len(metrics_df)}")
            print(f"   TTL: {self.cache_ttl_hours} horas")
            
            self._cleanup_old_caches()
            
        except Exception as e:
            print(f"Error guardando caché: {e}")
    
    def _cleanup_old_caches(self):
        """
        Limpia archivos de caché antiguos o con diferentes hashes.
        
        Mantiene solo el caché actual y elimina los demás.
        """
        if not self.cache_dir.exists():
            return
        
        current_cache_file = self._get_cache_filepath()
        
        # Buscar todos los archivos de caché
        cache_pattern = "district_metrics_*.pkl"
        cache_files = list(self.cache_dir.glob(cache_pattern))
        
        cleaned = 0
        for cache_file in cache_files:
            if cache_file != current_cache_file:
                try:
                    cache_file.unlink()
                    cleaned += 1
                except Exception as e:
                    print(f" No se pudo eliminar {cache_file.name}: {e}")
        
        if cleaned > 0:
            print(f"Limpieza: {cleaned} caché(s) antiguo(s) eliminado(s)")
    
    def invalidate_cache(self):
        """Elimina el archivo de caché."""
        cache_file = self._get_cache_filepath()
        if cache_file.exists():
            try:
                cache_file.unlink()
                print(f" Caché invalidado: {cache_file.name}")
            except Exception as e:
                print(f" Error invalidando caché: {e}")
        else:
            print("No hay caché para invalidar")

    # =================================================================
    
    def get_metrics_summary(self) -> pd.DataFrame:
        """
        Retorna resumen estadístico de las métricas.
        
        Returns:
            DataFrame con estadísticas descriptivas
        """
        if self.metrics_df is None:
            raise ValueError("No hay métricas calculadas. Usa analyze_all_districts() primero.")
        
        metric_columns = ['safety', 'transport', 'green', 'services']
        summary = self.metrics_df[metric_columns].describe()
        
        return summary
    
    def get_top_districts(self, metric: str, n: int = 5) -> pd.DataFrame:
        """
        Retorna los top N distritos según una métrica.
        
        Args:
            metric: Nombre de la métrica ('safety', 'transport', 'green', 'services')
            n: Número de distritos a retornar
        
        Returns:
            DataFrame con top N distritos
        """
        if self.metrics_df is None:
            raise ValueError("No hay métricas calculadas.")
        
        if metric not in self.metrics_df.columns:
            raise ValueError(f"Métrica '{metric}' no existe")
        
        top = self.metrics_df.nlargest(n, metric)[['district_name', metric]]
        
        return top