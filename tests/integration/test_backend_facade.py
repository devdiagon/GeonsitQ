import pytest
from unittest.mock import Mock, patch

from integration.backend_facade import RecommendationSystem


@pytest.mark.integration
class TestRecommendationSystemIntegration:
    
  @pytest.fixture
  def system(self, test_config_path, mock_city_graph):
    with patch('integration.backend_facade.CityGraph', return_value=mock_city_graph):
      return RecommendationSystem(config_path=str(test_config_path))
    
  def test_initialization(self, system):
    assert system.city is not None
    assert system.analyzer is not None
    assert system.strategies is not None
    assert len(system.strategies) > 0
    assert system.map_state is not None
    assert system.rec_observer is not None
    assert system.cache_observer is not None
    
  def test_set_strategy(self, system):
    success = system.set_strategy('quality_of_life')
    
    assert success is True
    assert system.current_strategy_name == 'quality_of_life'
    assert system.get_current_strategy() is not None
    
  def test_set_invalid_strategy(self, system):
    success = system.set_strategy('invalid_strategy')
    
    assert success is False
    
  def test_get_scores_df(self, system):
    system.set_strategy('quality_of_life')
    scores_df = system.get_scores_df()
    
    assert scores_df is not None
    assert 'score' in scores_df.columns
    assert 'rank' in scores_df.columns
    assert len(scores_df) > 0
    
  def test_get_top_districts(self, system):
    system.set_strategy('tourist')
    top5 = system.get_top_districts(5)
    
    assert top5 is not None
    assert len(top5) <= 5
    
    if len(top5) > 1:
      for i in range(len(top5) - 1):
        assert top5.iloc[i]['score'] >= top5.iloc[i + 1]['score']
    
  def test_get_district_details(self, system, mock_districts_gdf):
    system.set_strategy('convenience')
    
    district_name = mock_districts_gdf.iloc[0]['display_name']
    details = system.get_district_details(district_name)
    
    assert details is not None
    assert 'score' in details
    assert 'rank' in details
    assert 'metrics' in details
    
  def test_get_available_strategies(self, system):
    strategies = system.get_available_strategies()
    
    assert len(strategies) >= 3
    assert 'quality_of_life' in strategies
    assert 'tourist' in strategies
    assert 'convenience' in strategies
    
  def test_get_metrics_df(self, system):
    metrics_df = system.get_metrics_df()
    
    assert metrics_df is not None
    assert 'safety' in metrics_df.columns
    assert 'transport' in metrics_df.columns
    assert 'green' in metrics_df.columns
    assert 'services' in metrics_df.columns
    
  def test_get_system_status(self, system):
    status = system.get_system_status()
    
    assert 'num_districts' in status
    assert 'current_strategy' in status
    assert 'available_strategies' in status
    assert 'cache_enabled' in status
    assert 'observers_active' in status
    
    assert status['num_districts'] > 0
    assert len(status['available_strategies']) >= 3
    
  def test_strategy_change_updates_scores(self, system):
    system.set_strategy('quality_of_life')
    scores_1 = system.get_scores_df()
    
    system.set_strategy('tourist')
    scores_2 = system.get_scores_df()
    
    assert not scores_1['score'].equals(scores_2['score'])
    
  def test_invalidate_cache(self, system):
    system.invalidate_cache()
    
  def test_refresh_analysis(self, system):
    system.set_strategy('quality_of_life')
    
    scores_1 = system.get_scores_df()
    
    system.refresh_analysis()
    
    assert system.current_strategy_name == 'quality_of_life'
    
    scores_2 = system.get_scores_df()
    assert len(scores_1) == len(scores_2)


@pytest.mark.integration
@pytest.mark.slow
class TestRecommendationSystemPerformance:
    
  @pytest.fixture
  def system(self, test_config_path, mock_city_graph):
    with patch('integration.backend_facade.CityGraph', return_value=mock_city_graph):
      return RecommendationSystem(config_path=str(test_config_path))
    
  def test_multiple_strategy_switches(self, system):
    import time
    
    strategies = ['quality_of_life', 'tourist', 'convenience']
    
    start = time.time()
    for _ in range(3):
        for strategy_name in strategies:
            system.set_strategy(strategy_name)
            scores = system.get_scores_df()
            assert scores is not None
    
    elapsed = time.time() - start
    
    assert elapsed < 5.0