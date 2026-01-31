"""
Funciones para calcular métricas individuales de distritos.
Cada función es pura (stateless) y retorna un score normalizable.
"""

import geopandas as gpd
import numpy as np
from typing import Optional, Union
from shapely.geometry import Polygon, MultiPolygon

# Importar utilidades espaciales
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.spatial_utils import (
    points_in_polygon,
    calculate_area_coverage,
    find_nearest_feature,
    safe_spatial_join,
    get_polygon_centroid,
    calculate_density
)


def calculate_safety_score(
    district_polygon: Union[Polygon, MultiPolygon],
    crime_gdf: gpd.GeoDataFrame,
    gridcode_field: str = 'gridcode',
    invert_scale: bool = True
) -> float:
    """
    Calcula el score de seguridad de un distrito basado en zonas de criminalidad.
    
    El cálculo se hace mediante un promedio ponderado por área:
    - Se intersectan las zonas de criminalidad con el distrito
    - Se calcula el área de cada intersección
    - Se pondera el gridcode por el área correspondiente
    
    Args:
        district_polygon: Polígono del distrito a analizar
        crime_gdf: GeoDataFrame con zonas de criminalidad (debe tener campo 'gridcode')
        gridcode_field: Nombre del campo con el código de criminalidad
        invert_scale: Si True, invierte la escala (gridcode 1=seguro → score alto)
                     Si False, usa escala directa (gridcode 1 → score bajo)
    
    Returns:
        float: Score de seguridad (0.0 - 1.0)
               - 1.0 = Muy seguro
               - 0.0 = Muy inseguro
    
    Example:
        >>> safety = calculate_safety_score(district_polygon, crime_zones_gdf)
        >>> print(f"Seguridad: {safety * 100:.1f}%")
    
    Notes:
        - Según CONTEXT.md: gridcode 1 = seguro, gridcode 5 = muy inseguro
        - Por defecto invierte la escala para que score alto = seguro
        - Si no hay datos de criminalidad, retorna valor neutral (0.5)
    """
    if district_polygon is None or not district_polygon.is_valid:
        print("  Polígono de distrito inválido")
        return 0.5
    
    if crime_gdf is None or len(crime_gdf) == 0:
        print("  No hay datos de criminalidad")
        return 0.5
    
    try:
        # Validar que existe el campo gridcode
        if gridcode_field not in crime_gdf.columns:
            print(f"  Campo '{gridcode_field}' no encontrado en crime_gdf")
            return 0.5
        
        # Asegurar mismo CRS
        district_crs = 'EPSG:4326'
        if crime_gdf.crs != district_crs:
            crime_gdf = crime_gdf.to_crs(district_crs)
        
        # Filtrar zonas que intersectan con el distrito
        intersecting_crimes = crime_gdf[crime_gdf.intersects(district_polygon)].copy()
        
        if len(intersecting_crimes) == 0:
            return 0.5
        
        # Calcular intersecciones y áreas
        total_weighted_gridcode = 0.0
        total_area = 0.0
        
        for idx, crime_zone in intersecting_crimes.iterrows():
            try:
                # Calcular intersección
                intersection = district_polygon.intersection(crime_zone.geometry)
                
                if intersection.is_empty:
                    continue
                
                # Área de intersección
                area = intersection.area
                
                if area <= 0:
                    continue
                
                # Gridcode de esta zona
                gridcode = crime_zone[gridcode_field]
                
                # Validar que gridcode está en rango esperado (1-5)
                if not (1 <= gridcode <= 5):
                    print(f" Gridcode fuera de rango: {gridcode}")
                    continue
                
                # Acumular peso por área
                total_weighted_gridcode += gridcode * area
                total_area += area
                
            except Exception as e:
                print(f" Error procesando zona de crimen: {e}")
                continue
        
        if total_area == 0:
            return 0.5
        
        # Promedio ponderado
        avg_gridcode = total_weighted_gridcode / total_area
        
        # Normalizar a escala 0-1
        # gridcode está en rango 1-5, normalizar a 0-1
        if invert_scale:
            # gridcode 1 (seguro) → score 1.0
            # gridcode 5 (inseguro) → score 0.0
            # Fórmula: (max - valor) / (max - min) = (5 - gridcode) / 4
            safety_score = (5 - avg_gridcode) / 4.0
        else:
            # gridcode 1 → score 0.0
            # gridcode 5 → score 1.0
            safety_score = (avg_gridcode - 1) / 4.0
        
        # Asegurar que está en rango [0, 1]
        safety_score = np.clip(safety_score, 0.0, 1.0)
        
        return safety_score
        
    except Exception as e:
        print(f"Error calculando safety score: {e}")
        return 0.5


def calculate_transport_score(
    district_polygon: Union[Polygon, MultiPolygon],
    bus_stops_gdf: Optional[gpd.GeoDataFrame] = None,
    bus_routes_gdf: Optional[gpd.GeoDataFrame] = None,
    metro_stations_gdf: Optional[gpd.GeoDataFrame] = None,
    metro_line_gdf: Optional[gpd.GeoDataFrame] = None,
    route_id_field: str = 'Código_Ru',
    weights: Optional[dict] = None
) -> float:
    """
    Calcula el score de transporte de un distrito basado en:
    - Densidad de paradas de bus
    - Número de rutas de bus únicas que pasan
    - Proximidad/presencia de estaciones de metro
    
    Args:
        district_polygon: Polígono del distrito
        bus_stops_gdf: GeoDataFrame con paradas de bus
        bus_routes_gdf: GeoDataFrame con rutas de bus (LineStrings)
        metro_stations_gdf: GeoDataFrame con estaciones de metro
        metro_line_gdf: GeoDataFrame con línea de metro
        route_id_field: Campo que identifica rutas únicas de bus
        weights: Pesos para cada componente. Default:
                 {'bus_density': 0.4, 'route_connectivity': 0.3, 'metro': 0.3}
    
    Returns:
        float: Score de transporte (0.0 - 1.0)
    
    Example:
        >>> transport = calculate_transport_score(
        ...     district_polygon,
        ...     bus_stops_gdf=stops,
        ...     bus_routes_gdf=routes,
        ...     metro_stations_gdf=stations
        ... )
    
    Notes:
        - Si no hay datos de algún componente, su peso se redistribuye
        - Score final es combinación ponderada de los componentes disponibles
    """
    if district_polygon is None or not district_polygon.is_valid:
        print(" Polígono de distrito inválido")
        return 0.0
    
    # Pesos por defecto
    if weights is None:
        weights = {
            'bus_density': 0.4,
            'route_connectivity': 0.3,
            'metro': 0.3
        }
    
    try:
        scores = {}
        available_weights = {}
        
        # --- COMPONENTE 1: Densidad de paradas de bus ---
        if bus_stops_gdf is not None and len(bus_stops_gdf) > 0:
            # Contar paradas dentro del distrito
            stops_in_district = points_in_polygon(district_polygon, bus_stops_gdf)
            num_stops = len(stops_in_district)
            
            # Calcular densidad (paradas por km²)
            area_km2 = district_polygon.area / 1_000_000  # Convertir m² a km²
            
            if area_km2 > 0:
                density = num_stops / area_km2
                
                # Normalizar densidad a escala 0-1
                # Asumimos que 10 paradas/km² es "excelente"
                # Puedes ajustar este umbral según tu ciudad
                ideal_density = 10.0
                density_score = min(density / ideal_density, 1.0)
                
                scores['bus_density'] = density_score
                available_weights['bus_density'] = weights['bus_density']
            else:
                scores['bus_density'] = 0.0
                available_weights['bus_density'] = weights['bus_density']
        
        # --- COMPONENTE 2: Conectividad de rutas ---
        if bus_routes_gdf is not None and len(bus_routes_gdf) > 0:
            # Encontrar rutas que intersectan con el distrito
            routes_intersecting = bus_routes_gdf[
                bus_routes_gdf.intersects(district_polygon)
            ].copy()
            
            if len(routes_intersecting) > 0 and route_id_field in routes_intersecting.columns:
                # Contar rutas únicas
                unique_routes = routes_intersecting[route_id_field].nunique()
                
                # Normalizar: asumimos que 5+ rutas es excelente conectividad
                ideal_routes = 5.0
                connectivity_score = min(unique_routes / ideal_routes, 1.0)
                
                scores['route_connectivity'] = connectivity_score
                available_weights['route_connectivity'] = weights['route_connectivity']
            else:
                scores['route_connectivity'] = 0.0
                available_weights['route_connectivity'] = weights['route_connectivity']
        
        # --- COMPONENTE 3: Acceso a metro ---
        metro_score = 0.0
        has_metro_data = False
        
        if metro_stations_gdf is not None and len(metro_stations_gdf) > 0:
            # Verificar si hay estaciones dentro del distrito
            stations_in_district = points_in_polygon(district_polygon, metro_stations_gdf)
            num_stations = len(stations_in_district)
            
            if num_stations > 0:
                # Tiene estación(es) de metro: score máximo
                metro_score = 1.0
            else:
                # No tiene estación, calcular distancia a la más cercana
                centroid = get_polygon_centroid(district_polygon)
                if centroid is not None:
                    nearest = find_nearest_feature(centroid, metro_stations_gdf, max_distance=2000)
                    
                    if nearest is not None:
                        distance = nearest['distance']
                        # Normalizar: < 500m = bueno, > 2000m = malo
                        # Score decrece linealmente
                        if distance < 500:
                            metro_score = 0.8
                        elif distance < 1000:
                            metro_score = 0.6
                        elif distance < 2000:
                            metro_score = 0.3
                        else:
                            metro_score = 0.0
                    else:
                        metro_score = 0.0
            
            has_metro_data = True
        
        elif metro_line_gdf is not None and len(metro_line_gdf) > 0:
            # Si no hay datos de estaciones pero sí de la línea
            # Verificar si la línea cruza el distrito
            line_intersects = metro_line_gdf.intersects(district_polygon).any()
            
            if line_intersects:
                metro_score = 0.7  # Tiene línea pero sin estaciones específicas
            else:
                # Calcular distancia a la línea
                centroid = get_polygon_centroid(district_polygon)
                if centroid is not None:
                    min_distance = metro_line_gdf.geometry.distance(centroid).min()
                    
                    if min_distance < 1000:
                        metro_score = 0.4
                    elif min_distance < 2000:
                        metro_score = 0.2
                    else:
                        metro_score = 0.0
            
            has_metro_data = True
        
        if has_metro_data:
            scores['metro'] = metro_score
            available_weights['metro'] = weights['metro']
        
        # --- CALCULAR SCORE FINAL ---
        if len(scores) == 0:
            # No hay datos de transporte
            return 0.0
        
        # Normalizar pesos disponibles
        total_weight = sum(available_weights.values())
        if total_weight == 0:
            return 0.0
        
        # Score ponderado
        final_score = sum(
            scores[component] * (available_weights[component] / total_weight)
            for component in scores
        )
        
        # Asegurar rango [0, 1]
        final_score = np.clip(final_score, 0.0, 1.0)
        
        return final_score
        
    except Exception as e:
        print(f"Error calculando transport score: {e}")
        import traceback
        traceback.print_exc()
        return 0.0