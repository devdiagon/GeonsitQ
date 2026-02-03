import pytest

from observers.map_state import MapState
from observers.recommendation_observer import RecommendationObserver
from observers.cache_observer import CacheObserver
from analyzers.district_analyzer import DistrictAnalyzer


@pytest.mark.integration
@pytest.mark.observer
class TestMapStateWithObservers:
        
  @pytest.fixture
  def analyzer(self, test_config_path, mock_districts_gdf, mock_parks_gdf):
    analyzer = DistrictAnalyzer(config_path=str(test_config_path))
    analyzer.load_data(
      districts_gdf=mock_districts_gdf,
      parks_gdf=mock_parks_gdf
    )
    analyzer.analyze_all_districts(force_refresh=True)
    return analyzer
    
  @pytest.fixture
  def map_state_with_observers(self, analyzer):
    map_state = MapState()
    
    rec_observer = RecommendationObserver(analyzer)
    cache_observer = CacheObserver(analyzer)
    
    map_state.attach(rec_observer)
    map_state.attach(cache_observer)
    
    return map_state, rec_observer, cache_observer
    
  def test_strategy_change_notifies_observers(
    self, map_state_with_observers, mock_quality_strategy
  ):
    map_state, rec_observer, cache_observer = map_state_with_observers
    
    map_state.set_strategy(mock_quality_strategy)
    
    assert rec_observer.current_scores is not None
    assert len(rec_observer.current_scores) > 0
    
  def test_layer_change_invalidates_cache(self, map_state_with_observers):
    map_state, rec_observer, cache_observer = map_state_with_observers
    
    assert cache_observer.cache_valid is True
    
    map_state.set_active_layers({'crimes', 'parks'})
    
    assert cache_observer.cache_valid is False
    
  def test_multiple_observers_receive_notifications(
    self, analyzer, mock_quality_strategy
  ):
    map_state = MapState()
    
    obs1 = RecommendationObserver(analyzer)
    obs2 = RecommendationObserver(analyzer)
    obs3 = CacheObserver(analyzer)
    
    map_state.attach(obs1)
    map_state.attach(obs2)
    map_state.attach(obs3)
    
    map_state.set_strategy(mock_quality_strategy)
    
    assert obs1.current_scores is not None
    assert obs2.current_scores is not None
    
  def test_detach_observer_stops_notifications(
    self, map_state_with_observers, mock_quality_strategy
  ):
    map_state, rec_observer, cache_observer = map_state_with_observers
    
    map_state.detach(rec_observer)
    
    map_state.set_strategy(mock_quality_strategy)
    
    assert rec_observer.current_scores is None
    
  def test_disable_notifications_temporarily(
    self, map_state_with_observers, mock_quality_strategy
  ):
    map_state, rec_observer, cache_observer = map_state_with_observers
    
    map_state.disable_notifications()
    
    map_state.set_strategy(mock_quality_strategy)
    
    assert rec_observer.current_scores is None
    
    map_state.enable_notifications()
    map_state.set_strategy(mock_quality_strategy)
    
    assert rec_observer.current_scores is not None
    
  def test_reset_notifies_all_observers(
    self, map_state_with_observers, mock_quality_strategy
  ):
    map_state, rec_observer, cache_observer = map_state_with_observers
    
    map_state.set_strategy(mock_quality_strategy)
    assert rec_observer.current_scores is not None
    
    map_state.reset()
    
    assert cache_observer.cache_valid is False