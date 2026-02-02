import pytest
import pandas as pd

from analyzers.district_analyzer import DistrictAnalyzer


@pytest.mark.integration
class TestDistrictAnalyzerIntegration:
    
  @pytest.fixture
  def analyzer(self, test_config_path):
    return DistrictAnalyzer(config_path=str(test_config_path))
  
  @pytest.fixture
  def analyzer_with_data(self, analyzer, mock_districts_gdf, mock_parks_gdf, mock_tourist_places_gdf):
    analyzer.load_data(
      districts_gdf=mock_districts_gdf,
      parks_gdf=mock_parks_gdf,
      tourist_places_gdf=mock_tourist_places_gdf
    )
    return analyzer
  
  def test_load_data_success(self, analyzer, mock_districts_gdf):
    analyzer.load_data(districts_gdf=mock_districts_gdf)
    
    assert analyzer.districts_gdf is not None
    assert len(analyzer.districts_gdf) > 0
  
  def test_analyze_all_districts(self, analyzer_with_data):
    metrics_df = analyzer_with_data.analyze_all_districts(force_refresh=True)
    
    assert metrics_df is not None
    assert len(metrics_df) > 0
    
    expected_cols = ['district_name', 'safety', 'transport', 'green', 'services']
    for col in expected_cols:
      assert col in metrics_df.columns
    
    for col in ['safety', 'transport', 'green', 'services']:
      assert metrics_df[col].min() >= 0.0
      assert metrics_df[col].max() <= 1.0
  
  def test_cache_functionality(self, analyzer_with_data):
    import time
    
    start = time.time()
    metrics_1 = analyzer_with_data.analyze_all_districts(force_refresh=True)
    time_no_cache = time.time() - start
    
    start = time.time()
    metrics_2 = analyzer_with_data.analyze_all_districts(force_refresh=False)
    time_with_cache = time.time() - start
    
    pd.testing.assert_frame_equal(
      metrics_1[['safety', 'transport', 'green', 'services']],
      metrics_2[['safety', 'transport', 'green', 'services']]
    )
    
    assert time_with_cache < time_no_cache
  
  def test_get_metrics_summary(self, analyzer_with_data):
    analyzer_with_data.analyze_all_districts(force_refresh=True)
    summary = analyzer_with_data.get_metrics_summary()
    
    assert summary is not None
    assert 'safety' in summary
    assert 'mean' in summary['safety']
    assert 'std' in summary['safety']
    assert 'min' in summary['safety']
    assert 'max' in summary['safety']
  
  def test_get_top_districts(self, analyzer_with_data):
    analyzer_with_data.analyze_all_districts(force_refresh=True)
      
    top_safety = analyzer_with_data.get_top_districts('safety', n=2)
      
    assert top_safety is not None
    assert len(top_safety) <= 2

    if len(top_safety) > 1:
      assert top_safety.iloc[0]['safety'] >= top_safety.iloc[1]['safety']
  
  def test_invalidate_cache(self, analyzer_with_data):
    analyzer_with_data.analyze_all_districts(force_refresh=True)
    
    cache_info = analyzer_with_data.get_cache_info()
    assert cache_info['exists'] is True
    
    analyzer_with_data.invalidate_cache()
    
    cache_info = analyzer_with_data.get_cache_info()
    assert cache_info['exists'] is False
  
  def test_get_cache_info(self, analyzer_with_data):
    analyzer_with_data.analyze_all_districts(force_refresh=True)
    
    info = analyzer_with_data.get_cache_info()
    
    assert 'cache_file' in info
    assert 'exists' in info
    assert 'enabled' in info
    assert 'ttl_hours' in info