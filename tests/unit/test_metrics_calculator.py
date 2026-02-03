import pytest
import geopandas as gpd

from analyzers.metrics_calculator import (
  calculate_safety_score,
  calculate_transport_score,
  calculate_green_score,
  calculate_services_score
)


@pytest.mark.unit
class TestSafetyScore:  
  def test_safety_score_calculation(self, mock_districts_gdf, mock_crime_gdf):
    district = mock_districts_gdf.iloc[0].geometry
    score = calculate_safety_score(district, mock_crime_gdf)
    
    assert 0.0 <= score <= 1.0
  
  def test_safety_score_invert_scale(self, mock_districts_gdf, mock_crime_gdf):
    district = mock_districts_gdf.iloc[0].geometry
    
    score_inverted = calculate_safety_score(
      district, mock_crime_gdf, invert_scale=True
    )
    score_normal = calculate_safety_score(
      district, mock_crime_gdf, invert_scale=False
    )
    
    assert score_inverted != score_normal
  
  def test_safety_score_no_crime_data(self, mock_districts_gdf):
    district = mock_districts_gdf.iloc[0].geometry
    empty_crime = gpd.GeoDataFrame()
    
    score = calculate_safety_score(district, empty_crime)
    assert score == 0.5


@pytest.mark.unit
class TestTransportScore:    
  def test_transport_score_with_buses(
    self, mock_districts_gdf, mock_bus_stops_gdf
  ):
    district = mock_districts_gdf.iloc[0].geometry
    
    score = calculate_transport_score(
      district,
      bus_stops_gdf=mock_bus_stops_gdf
    )
    
    assert 0.0 <= score <= 1.0
    
  def test_transport_score_no_data(self, mock_districts_gdf):
    district = mock_districts_gdf.iloc[0].geometry
    
    score = calculate_transport_score(district)
    assert score == 0.0


@pytest.mark.unit
class TestGreenScore:    
  def test_green_score_with_parks(self, mock_districts_gdf, mock_parks_gdf):
    district = mock_districts_gdf.iloc[0].geometry
    
    score = calculate_green_score(district, mock_parks_gdf)
    
    assert 0.0 <= score <= 1.0
    
  def test_green_score_min_area_filter(self, mock_districts_gdf, mock_parks_gdf):
    district = mock_districts_gdf.iloc[0].geometry
    
    score = calculate_green_score(
      district, mock_parks_gdf, min_park_area=1e10
    )
    assert score == 0.0


@pytest.mark.unit
class TestServicesScore:    
  def test_services_score(self, mock_districts_gdf, mock_tourist_places_gdf):
    district = mock_districts_gdf.iloc[0].geometry
    
    score = calculate_services_score(district, mock_tourist_places_gdf)
    
    assert 0.0 <= score <= 1.0