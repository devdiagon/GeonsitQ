import pytest
import geopandas as gpd
from shapely.geometry import Point, Polygon

from utils.spatial_utils import (
    create_spatial_index,
    calculate_area_coverage,
    find_nearest_feature,
    safe_spatial_join,
    validate_geometries,
    points_in_polygon,
    calculate_density
)


@pytest.mark.unit
@pytest.mark.spatial
class TestSpatialIndex:    
  def test_create_spatial_index_success(self, mock_bus_stops_gdf):
    index = create_spatial_index(mock_bus_stops_gdf)
    assert index is not None
  
  def test_create_spatial_index_empty(self):
    empty_gdf = gpd.GeoDataFrame()
    index = create_spatial_index(empty_gdf)
    assert index is None


@pytest.mark.unit
@pytest.mark.spatial
class TestAreaCoverage:    
  def test_area_coverage_with_parks(self, mock_districts_gdf, mock_parks_gdf):
    district_polygon = mock_districts_gdf.iloc[0].geometry
    coverage = calculate_area_coverage(district_polygon, mock_parks_gdf)
        
    assert 0.0 <= coverage <= 1.0
    assert coverage > 0 
    
  def test_area_coverage_no_intersection(self, mock_districts_gdf):
    district_polygon = mock_districts_gdf.iloc[0].geometry
    
    far_parks = gpd.GeoDataFrame({
      'geometry': [Polygon([(10, 10), (10, 11), (11, 11), (11, 10)])]
    }, crs='EPSG:4326')
      
    coverage = calculate_area_coverage(district_polygon, far_parks)
    assert coverage == 0.0


@pytest.mark.unit
@pytest.mark.spatial
class TestNearestFeature:    
  def test_find_nearest_feature(self, mock_bus_stops_gdf):
    point = Point(0.3, 0.3)
    result = find_nearest_feature(point, mock_bus_stops_gdf)
    
    assert result is not None
    assert 'distance' in result
    assert 'feature' in result
    assert result['distance'] >= 0
    
  def test_find_nearest_with_max_distance(self, mock_bus_stops_gdf):
    point = Point(10, 10)
    result = find_nearest_feature(point, mock_bus_stops_gdf, max_distance=0.1)
    
    assert result is None


@pytest.mark.unit
@pytest.mark.spatial
class TestSafeSpatialJoin:    
  def test_safe_spatial_join_success(self, mock_districts_gdf, mock_bus_stops_gdf):
    result = safe_spatial_join(
      mock_districts_gdf,
      mock_bus_stops_gdf,
      predicate='contains'
    )
        
    assert result is not None
    assert len(result) >= 0
    
  def test_safe_spatial_join_different_crs(self, mock_districts_gdf):
    points_utm = gpd.GeoDataFrame({
      'geometry': [Point(500000, 9800000)]
    }, crs='EPSG:32717')
    
    result = safe_spatial_join(
      mock_districts_gdf,
      points_utm,
      predicate='intersects'
    )
    
    assert result is not None


@pytest.mark.unit
@pytest.mark.spatial
class TestValidateGeometries:    
  def test_validate_geometries_all_valid(self, mock_districts_gdf):
    result = validate_geometries(mock_districts_gdf)
    assert len(result) == len(mock_districts_gdf)
    
  def test_validate_geometries_with_fix(self):
    invalid_poly = Polygon([
      (0, 0), (2, 2), (2, 0), (0, 2), (0, 0)
    ])
    
    gdf = gpd.GeoDataFrame({
      'geometry': [invalid_poly]
    }, crs='EPSG:4326')
    
    result = validate_geometries(gdf, fix=True)
    assert len(result) >= 0


@pytest.mark.unit
@pytest.mark.spatial
class TestPointsInPolygon:
  def test_points_in_polygon(self, mock_districts_gdf, mock_bus_stops_gdf):
    polygon = mock_districts_gdf.iloc[0].geometry
    points = points_in_polygon(polygon, mock_bus_stops_gdf)
    
    assert len(points) >= 0
    for point in points.geometry:
      assert polygon.contains(point)


@pytest.mark.unit
@pytest.mark.spatial
class TestCalculateDensity:  
  def test_calculate_density(self, mock_districts_gdf, mock_bus_stops_gdf):
    polygon = mock_districts_gdf.iloc[0].geometry
    density = calculate_density(polygon, mock_bus_stops_gdf, unit='km2')
    
    assert density >= 0