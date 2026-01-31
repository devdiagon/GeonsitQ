"""
Funciones para normalización de métricas a escalas comparables.
"""

import numpy as np
import pandas as pd
from typing import Union, List, Optional


def normalize_min_max(
    values: Union[np.ndarray, pd.Series, List[float]],
    feature_range: tuple = (0.0, 1.0)
) -> np.ndarray:
    """
    Normalización Min-Max a un rango específico.
    
    Formula: X_scaled = (X - X_min) / (X_max - X_min) * (max - min) + min
    
    Args:
        values: Array de valores a normalizar
        feature_range: Rango objetivo (min, max). Default: (0, 1)
    
    Returns:
        np.ndarray: Valores normalizados
    
    Example:
        >>> values = [1, 2, 3, 4, 5]
        >>> normalized = normalize_min_max(values)
        >>> # Output: [0.0, 0.25, 0.5, 0.75, 1.0]
    """
    values = np.array(values, dtype=float)
    
    # Manejar caso de valores constantes
    if np.all(values == values[0]):
        # Todos los valores son iguales, retornar punto medio del rango
        mid_point = (feature_range[0] + feature_range[1]) / 2
        return np.full_like(values, mid_point)
    
    # Normalización estándar
    min_val = np.nanmin(values)
    max_val = np.nanmax(values)
    
    if max_val == min_val:
        # Evitar división por cero
        mid_point = (feature_range[0] + feature_range[1]) / 2
        return np.full_like(values, mid_point)
    
    # Escalar a [0, 1]
    values_scaled = (values - min_val) / (max_val - min_val)
    
    # Escalar al rango deseado
    range_min, range_max = feature_range
    values_scaled = values_scaled * (range_max - range_min) + range_min
    
    return values_scaled


def normalize_z_score(
    values: Union[np.ndarray, pd.Series, List[float]],
    clip_std: Optional[float] = 3.0
) -> np.ndarray:
    """
    Normalización Z-Score (estandarización).
    
    Formula: Z = (X - mean) / std
    
    Args:
        values: Array de valores a normalizar
        clip_std: Si se especifica, recorta valores a ±clip_std desviaciones
    
    Returns:
        np.ndarray: Valores estandarizados
    
    Example:
        >>> values = [1, 2, 3, 4, 5, 100]  # 100 es outlier
        >>> normalized = normalize_z_score(values, clip_std=3.0)
    """
    values = np.array(values, dtype=float)
    
    mean = np.nanmean(values)
    std = np.nanstd(values)
    
    if std == 0:
        # Sin varianza, retornar ceros
        return np.zeros_like(values)
    
    z_scores = (values - mean) / std
    
    if clip_std is not None:
        z_scores = np.clip(z_scores, -clip_std, clip_std)
    
    return z_scores


def safe_normalize(
    value: float,
    min_val: float,
    max_val: float,
    neutral_value: float = 0.5
) -> float:
    """
    Normalización segura de un valor individual con manejo de casos edge.
    
    Args:
        value: Valor a normalizar
        min_val: Valor mínimo del rango
        max_val: Valor máximo del rango
        neutral_value: Valor a retornar si min == max
    
    Returns:
        float: Valor normalizado entre 0 y 1
    
    Example:
        >>> normalized = safe_normalize(75, 0, 100)
        >>> # Output: 0.75
    """
    # Validar inputs
    if pd.isna(value) or pd.isna(min_val) or pd.isna(max_val):
        return neutral_value
    
    # Si min y max son iguales
    if max_val == min_val:
        return neutral_value
    
    # Normalizar
    normalized = (value - min_val) / (max_val - min_val)
    
    # Asegurar rango [0, 1]
    normalized = np.clip(normalized, 0.0, 1.0)
    
    return normalized


def invert_scale(
    values: Union[np.ndarray, pd.Series, List[float]],
    scale_range: tuple = (0.0, 1.0)
) -> np.ndarray:
    """
    Invierte una escala de valores.
    Útil cuando un valor alto significa algo negativo (ej: criminalidad).
    
    Formula: X_inverted = max - X + min
    
    Args:
        values: Array de valores a invertir
        scale_range: Rango de la escala (min, max). Default: (0, 1)
    
    Returns:
        np.ndarray: Valores invertidos
    
    Example:
        >>> values = [0.2, 0.5, 0.8, 1.0]
        >>> inverted = invert_scale(values)
        >>> # Output: [0.8, 0.5, 0.2, 0.0]
    """
    values = np.array(values, dtype=float)
    range_min, range_max = scale_range
    
    # Invertir: max - value + min
    inverted = range_max - values + range_min
    
    return inverted


def normalize_with_weights(
    metrics_dict: dict,
    weights: dict,
    method: str = 'min_max'
) -> dict:
    """
    Normaliza un diccionario de métricas y aplica pesos.
    
    Args:
        metrics_dict: Dict con métricas por distrito
                     Formato: {metric_name: [values]}
        weights: Dict con pesos por métrica
                Formato: {metric_name: weight}
        method: Método de normalización ('min_max' o 'z_score')
    
    Returns:
        dict: Dict con métricas normalizadas y ponderadas
    
    Example:
        >>> metrics = {'safety': [0.3, 0.7, 0.9], 'transport': [0.5, 0.6, 0.8]}
        >>> weights = {'safety': 0.6, 'transport': 0.4}
        >>> normalized = normalize_with_weights(metrics, weights)
    """
    normalized_metrics = {}
    
    for metric_name, values in metrics_dict.items():
        if metric_name not in weights:
            print(f" Métrica '{metric_name}' no tiene peso asignado, se omite")
            continue
        
        values_array = np.array(values, dtype=float)
        
        # Normalizar según método
        if method == 'min_max':
            normalized = normalize_min_max(values_array)
        elif method == 'z_score':
            normalized = normalize_z_score(values_array)
            # Convertir z-scores a [0, 1]
            normalized = normalize_min_max(normalized)
        else:
            raise ValueError(f"Método de normalización desconocido: {method}")
        
        # Aplicar peso
        weight = weights[metric_name]
        weighted = normalized * weight
        
        normalized_metrics[metric_name] = weighted
    
    return normalized_metrics


def handle_missing_values(
    values: Union[np.ndarray, pd.Series],
    strategy: str = 'neutral'
) -> np.ndarray:
    """
    Maneja valores faltantes (NaN) en un array.
    
    Args:
        values: Array con posibles NaN
        strategy: Estrategia de imputación:
                 - 'neutral': Reemplazar con 0.5
                 - 'zero': Reemplazar con 0.0
                 - 'mean': Reemplazar con media de valores válidos
                 - 'median': Reemplazar con mediana
    
    Returns:
        np.ndarray: Array sin NaN
    
    Example:
        >>> values = [0.3, np.nan, 0.7, 0.9]
        >>> handled = handle_missing_values(values, strategy='mean')
        >>> # Output: [0.3, 0.633, 0.7, 0.9]
    """
    values = np.array(values, dtype=float)
    
    if not np.any(np.isnan(values)):
        # No hay NaN, retornar
        return values
    
    if strategy == 'neutral':
        fill_value = 0.5
    elif strategy == 'zero':
        fill_value = 0.0
    elif strategy == 'mean':
        fill_value = np.nanmean(values)
        if np.isnan(fill_value):
            fill_value = 0.5  # Fallback si todos son NaN
    elif strategy == 'median':
        fill_value = np.nanmedian(values)
        if np.isnan(fill_value):
            fill_value = 0.5  # Fallback
    else:
        raise ValueError(f"Estrategia desconocida: {strategy}")
    
    # Reemplazar NaN
    values_filled = np.where(np.isnan(values), fill_value, values)
    
    return values_filled


def robust_normalize(
    values: Union[np.ndarray, pd.Series, List[float]],
    percentile_range: tuple = (5, 95)
) -> np.ndarray:
    """
    Normalización robusta usando percentiles (resistente a outliers).
    
    Args:
        values: Array de valores a normalizar
        percentile_range: Percentiles a usar (min, max). Default: (5, 95)
    
    Returns:
        np.ndarray: Valores normalizados robustamente
    
    Example:
        >>> values = [1, 2, 3, 4, 5, 100]  # 100 es outlier
        >>> normalized = robust_normalize(values)
        >>> # Usa percentiles para ignorar el outlier
    """
    values = np.array(values, dtype=float)
    
    # Calcular percentiles
    p_min, p_max = percentile_range
    lower = np.nanpercentile(values, p_min)
    upper = np.nanpercentile(values, p_max)
    
    if upper == lower:
        # Sin rango, retornar 0.5
        return np.full_like(values, 0.5)
    
    # Normalizar usando percentiles
    normalized = (values - lower) / (upper - lower)
    
    # Clip a [0, 1]
    normalized = np.clip(normalized, 0.0, 1.0)
    
    return normalized