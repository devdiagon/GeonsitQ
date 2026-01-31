"""
Utilidades para operaciones espaciales con GeoPandas.
Funciones auxiliares para análisis geográfico.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.strtree import STRtree
from typing import Union, Optional, List
import warnings

warnings.filterwarnings('ignore', category=UserWarning)


def create_spatial_index(gdf: gpd.GeoDataFrame) -> STRtree:
    """
    Crea un índice espacial STRtree para búsquedas rápidas.
    
    Args:
        gdf: GeoDataFrame con geometrías
        
    Returns:
        STRtree: Índice espacial para consultas rápidas
        
    Example:
        >>> tree = create_spatial_index(bus_stops_gdf)
        >>> nearby = tree.query(district_polygon)
    """
    if gdf is None or len(gdf) == 0:
        return None
    
    try:
        # Asegurar que las geometrías son válidas
        valid_geoms = gdf[gdf.geometry.is_valid].geometry.values
        if len(valid_geoms) == 0:
            return None
        return STRtree(valid_geoms)
    except Exception as e:
        print(f"Error creando índice espacial: {e}")
        return None


def calculate_area_coverage(
    polygon: Union[Polygon, MultiPolygon],
    layer_gdf: gpd.GeoDataFrame
) -> float:
    """
    Calcula el porcentaje de área del polígono cubierta por geometrías de una capa.
    
    Args:
        polygon: Polígono de referencia (ej: distrito)
        layer_gdf: GeoDataFrame con geometrías a evaluar (ej: parques)
        
    Returns:
        float: Porcentaje de cobertura (0.0 - 1.0)
        
    Example:
        >>> coverage = calculate_area_coverage(district_polygon, parks_gdf)
        >>> print(f"Cobertura de parques: {coverage * 100:.1f}%")
    """
    if polygon is None or not polygon.is_valid:
        return 0.0
    
    if layer_gdf is None or len(layer_gdf) == 0:
        return 0.0
    
    try:
        # Asegurar mismo CRS
        polygon_area = polygon.area
        if polygon_area == 0:
            return 0.0
        
        # Filtrar geometrías que intersectan
        intersecting = layer_gdf[layer_gdf.intersects(polygon)]
        
        if len(intersecting) == 0:
            return 0.0
        
        # Calcular área total de intersección
        total_intersection_area = 0.0
        for geom in intersecting.geometry:
            if geom.is_valid:
                intersection = polygon.intersection(geom)
                total_intersection_area += intersection.area
        
        # Calcular porcentaje
        coverage = min(total_intersection_area / polygon_area, 1.0)
        return coverage
        
    except Exception as e:
        print(f"Error calculando cobertura de área: {e}")
        return 0.0


def find_nearest_feature(
    point: Point,
    features_gdf: gpd.GeoDataFrame,
    max_distance: Optional[float] = None
) -> Optional[dict]:
    """
    Encuentra la feature más cercana a un punto.
    
    Args:
        point: Punto de referencia
        features_gdf: GeoDataFrame con features a buscar
        max_distance: Distancia máxima de búsqueda (metros/grados según CRS)
        
    Returns:
        dict: {'distance': float, 'feature': GeoSeries} o None si no hay features
        
    Example:
        >>> nearest = find_nearest_feature(district_centroid, metro_stations_gdf)
        >>> print(f"Estación más cercana: {nearest['feature']['nam']}")
    """
    if features_gdf is None or len(features_gdf) == 0:
        return None
    
    try:
        # Calcular distancias
        distances = features_gdf.geometry.distance(point)
        
        if len(distances) == 0:
            return None
        
        # Encontrar mínima distancia
        min_idx = distances.idxmin()
        min_distance = distances[min_idx]
        
        # Verificar max_distance si está definido
        if max_distance is not None and min_distance > max_distance:
            return None
        
        return {
            'distance': min_distance,
            'feature': features_gdf.loc[min_idx]
        }
        
    except Exception as e:
        print(f"Error buscando feature más cercana: {e}")
        return None


def safe_spatial_join(
    gdf1: gpd.GeoDataFrame,
    gdf2: gpd.GeoDataFrame,
    how: str = 'inner',
    predicate: str = 'intersects',
    **kwargs
) -> gpd.GeoDataFrame:
    """
    Realiza un spatial join con validación de CRS y geometrías.
    
    Args:
        gdf1: Primer GeoDataFrame
        gdf2: Segundo GeoDataFrame
        how: Tipo de join ('inner', 'left', 'right')
        predicate: Predicado espacial ('intersects', 'within', 'contains')
        **kwargs: Argumentos adicionales para sjoin
        
    Returns:
        GeoDataFrame: Resultado del join
        
    Example:
        >>> stops_in_districts = safe_spatial_join(
        ...     districts_gdf, 
        ...     bus_stops_gdf, 
        ...     predicate='contains'
        ... )
    """
    if gdf1 is None or gdf2 is None:
        return gpd.GeoDataFrame()
    
    if len(gdf1) == 0 or len(gdf2) == 0:
        return gpd.GeoDataFrame()
    
    try:
        # Verificar CRS
        if gdf1.crs != gdf2.crs:
            print(f" CRS diferente detectado. Reproyectando gdf2 de {gdf2.crs} a {gdf1.crs}")
            gdf2 = gdf2.to_crs(gdf1.crs)
        
        # Filtrar geometrías inválidas
        gdf1_valid = gdf1[gdf1.geometry.is_valid].copy()
        gdf2_valid = gdf2[gdf2.geometry.is_valid].copy()
        
        if len(gdf1_valid) == 0 or len(gdf2_valid) == 0:
            print(" No hay geometrías válidas para el join")
            return gpd.GeoDataFrame()
        
        # Realizar spatial join
        result = gpd.sjoin(gdf1_valid, gdf2_valid, how=how, predicate=predicate, **kwargs)
        
        return result
        
    except Exception as e:
        print(f"Error en spatial join: {e}")
        return gpd.GeoDataFrame()


def validate_geometries(gdf: gpd.GeoDataFrame, fix: bool = False) -> gpd.GeoDataFrame:
    """
    Valida y opcionalmente repara geometrías inválidas.
    
    Args:
        gdf: GeoDataFrame a validar
        fix: Si True, intenta reparar geometrías inválidas
        
    Returns:
        GeoDataFrame: GeoDataFrame validado (y posiblemente reparado)
        
    Example:
        >>> clean_gdf = validate_geometries(raw_gdf, fix=True)
    """
    if gdf is None or len(gdf) == 0:
        return gdf
    
    try:
        # Identificar geometrías inválidas
        invalid_mask = ~gdf.geometry.is_valid
        num_invalid = invalid_mask.sum()
        
        if num_invalid > 0:
            print(f" Encontradas {num_invalid} geometrías inválidas de {len(gdf)}")
            
            if fix:
                print("Intentando reparar geometrías...")
                # Usar buffer(0) para reparar geometrías simples
                gdf.loc[invalid_mask, 'geometry'] = gdf.loc[invalid_mask, 'geometry'].buffer(0)
                
                # Verificar nuevamente
                still_invalid = ~gdf.geometry.is_valid
                if still_invalid.sum() > 0:
                    print(f" {still_invalid.sum()} geometrías no pudieron repararse, se eliminarán")
                    gdf = gdf[gdf.geometry.is_valid].copy()
                else:
                    print("Todas las geometrías reparadas exitosamente")
            else:
                print(" Usa fix=True para intentar reparar automáticamente")
        
        return gdf
        
    except Exception as e:
        print(f"Error validando geometrías: {e}")
        return gdf


def points_in_polygon(
    polygon: Union[Polygon, MultiPolygon],
    points_gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Encuentra todos los puntos que están dentro de un polígono.
    Optimizado con índice espacial para grandes datasets.
    
    Args:
        polygon: Polígono de referencia
        points_gdf: GeoDataFrame con puntos
        
    Returns:
        GeoDataFrame: Puntos que están dentro del polígono
        
    Example:
        >>> stops_in_district = points_in_polygon(district_polygon, bus_stops_gdf)
    """
    if polygon is None or not polygon.is_valid:
        return gpd.GeoDataFrame()
    
    if points_gdf is None or len(points_gdf) == 0:
        return gpd.GeoDataFrame()
    
    try:
        # Usar spatial index para primera pasada (bbox)
        tree = create_spatial_index(points_gdf)
        if tree is None:
            # Fallback sin índice
            return points_gdf[points_gdf.within(polygon)].copy()
        
        # Consulta con bbox (rápida)
        candidate_indices = tree.query(polygon)
        
        if len(candidate_indices) == 0:
            return gpd.GeoDataFrame()
        
        # Filtrar candidatos con verificación exacta
        candidates = points_gdf.iloc[candidate_indices]
        result = candidates[candidates.within(polygon)].copy()
        
        return result
        
    except Exception as e:
        print(f"Error en points_in_polygon: {e}")
        return gpd.GeoDataFrame()


def calculate_density(
    polygon: Union[Polygon, MultiPolygon],
    features_gdf: gpd.GeoDataFrame,
    unit: str = 'km2'
) -> float:
    """
    Calcula la densidad de features por unidad de área.
    
    Args:
        polygon: Polígono de referencia
        features_gdf: GeoDataFrame con features a contar
        unit: Unidad de área ('km2' o 'm2')
        
    Returns:
        float: Densidad (features por unidad de área)
        
    Example:
        >>> density = calculate_density(district_polygon, bus_stops_gdf, unit='km2')
        >>> print(f"Densidad de paradas: {density:.2f} paradas/km²")
    """
    if polygon is None or not polygon.is_valid:
        return 0.0
    
    try:
        # Contar features dentro del polígono
        features_inside = points_in_polygon(polygon, features_gdf)
        count = len(features_inside)
        
        # Calcular área
        area = polygon.area
        
        # Convertir a unidad solicitada si es necesario
        if unit == 'km2':
            # Asumiendo que el área está en m² (típico de UTM)
            area = area / 1_000_000  # Convertir a km²
        
        if area == 0:
            return 0.0
        
        density = count / area
        return density
        
    except Exception as e:
        print(f"Error calculando densidad: {e}")
        return 0.0


def get_polygon_centroid(polygon: Union[Polygon, MultiPolygon]) -> Optional[Point]:
    """
    Obtiene el centroide de un polígono.
    
    Args:
        polygon: Polígono
        
    Returns:
        Point: Centroide del polígono o None si es inválido
    """
    if polygon is None or not polygon.is_valid:
        return None
    
    try:
        return polygon.centroid
    except Exception as e:
        print(f"Error calculando centroide: {e}")
        return None


def ensure_crs(gdf: gpd.GeoDataFrame, target_crs: str = 'EPSG:4326') -> gpd.GeoDataFrame:
    """
    Asegura que un GeoDataFrame esté en el CRS objetivo.
    
    Args:
        gdf: GeoDataFrame a verificar/reproyectar
        target_crs: CRS objetivo (default: EPSG:4326 para Folium)
        
    Returns:
        GeoDataFrame: GeoDataFrame en el CRS objetivo
    """
    if gdf is None or len(gdf) == 0:
        return gdf
    
    try:
        if gdf.crs is None:
            print(f"GeoDataFrame sin CRS definido, asumiendo {target_crs}")
            gdf = gdf.set_crs(target_crs)
        elif gdf.crs != target_crs:
            gdf = gdf.to_crs(target_crs)
        
        return gdf
        
    except Exception as e:
        print(f"Error asegurando CRS: {e}")
        return gdf