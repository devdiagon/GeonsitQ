import pytest
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


# ========== FIXTURES DE CONFIGURACIÓN ==========

@pytest.fixture(scope="session")
def test_config_path():
    return Path(__file__).parent / 'fixtures' / 'test_config.yaml'


@pytest.fixture(scope="session")
def test_data_dir():
    return Path(__file__).parent / 'fixtures'


# ========== FIXTURES DE GEODATAFRAMES ==========

@pytest.fixture
def mock_districts_gdf():
    districts = {
        'display_name': ['Distrito A', 'Distrito B', 'Distrito C'],
        'geometry': [
            Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]),
            Polygon([(1, 0), (1, 1), (2, 1), (2, 0)]),
            Polygon([(0, 1), (0, 2), (1, 2), (1, 1)])
        ]
    }
    return gpd.GeoDataFrame(districts, crs='EPSG:4326')


@pytest.fixture
def mock_crime_gdf():
    crimes = {
        'gridcode': [1, 3, 5],
        'geometry': [
            Polygon([(0, 0), (0, 0.5), (0.5, 0.5), (0.5, 0)]),
            Polygon([(1, 0), (1, 0.5), (1.5, 0.5), (1.5, 0)]),
            Polygon([(0, 1), (0, 1.5), (0.5, 1.5), (0.5, 1)])
        ]
    }
    return gpd.GeoDataFrame(crimes, crs='EPSG:4326')


@pytest.fixture
def mock_parks_gdf():
    parks = {
        'name': ['Park A', 'Park B'],
        'geometry': [
            Polygon([(0.2, 0.2), (0.2, 0.4), (0.4, 0.4), (0.4, 0.2)]),
            Polygon([(1.2, 0.2), (1.2, 0.4), (1.4, 0.4), (1.4, 0.2)])
        ]
    }
    gdf = gpd.GeoDataFrame(parks, crs='EPSG:4326')
    gdf['area'] = gdf.geometry.area
    return gdf


@pytest.fixture
def mock_bus_stops_gdf():
    stops = {
        'objectid': [1, 2, 3, 4],
        'geometry': [
            Point(0.3, 0.3),
            Point(0.7, 0.7),
            Point(1.3, 0.3),
            Point(1.7, 0.7)
        ]
    }
    return gpd.GeoDataFrame(stops, crs='EPSG:4326')


@pytest.fixture
def mock_tourist_places_gdf():
    places = {
        'tourism': ['museum', 'attraction'],
        'shop': [None, 'mall'],
        'geometry': [
            Point(0.5, 0.5),
            Point(1.5, 0.5)
        ]
    }
    return gpd.GeoDataFrame(places, crs='EPSG:4326')


# ========== FIXTURES DE DATAFRAMES ==========

@pytest.fixture
def mock_scores_df():
    return pd.DataFrame({
        'district_id': [0, 1, 2],
        'district_name': ['Distrito A', 'Distrito B', 'Distrito C'],
        'safety': [0.8, 0.6, 0.4],
        'transport': [0.7, 0.8, 0.5],
        'green': [0.6, 0.4, 0.7],
        'services': [0.5, 0.7, 0.6],
        'score': [0.75, 0.68, 0.55],
        'rank': [1, 2, 3]
    })


# ========== FIXTURES DE ESTRATEGIAS ==========

@pytest.fixture
def mock_quality_strategy():
    from strategies.qol_strategy import QualityOfLifeStrategy
    return QualityOfLifeStrategy()


@pytest.fixture
def mock_tourist_strategy():
    from strategies.tourist_strategy import TouristStrategy
    return TouristStrategy()


@pytest.fixture
def all_strategies():
    from strategies.strategy_factory import StrategyFactory
    return StrategyFactory.create_all_strategies()


# ========== FIXTURES DE COMPONENTES ==========

@pytest.fixture
def mock_map_state():
    from observers.map_state import MapState
    return MapState()


@pytest.fixture
def mock_cache_manager(tmp_path):
    from utils.cache_manager import CacheManager
    return CacheManager(cache_dir=str(tmp_path), ttl_hours=1)

@pytest.fixture
def mock_city_graph(mock_districts_gdf, mock_parks_gdf, mock_tourist_places_gdf):
    from unittest.mock import Mock
    
    mock_city = Mock()
    
    mock_city.get_graph.return_value = mock_districts_gdf
    mock_city.get_parks.return_value = mock_parks_gdf
    mock_city.get_tourist_places.return_value = mock_tourist_places_gdf
    mock_city.get_places.return_value = mock_districts_gdf['display_name'].tolist()
    
    mock_city.get_city_name.return_value = "City"
    mock_city.get_districts_names.return_value = mock_districts_gdf['display_name'].tolist()
    mock_city.get_bounds.return_value = tuple(mock_districts_gdf.total_bounds)
    
    return mock_city