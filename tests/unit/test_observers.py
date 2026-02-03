import pytest
from unittest.mock import Mock, MagicMock

from observers.map_state import MapState, Observer
from observers.recommendation_observer import RecommendationObserver
from observers.cache_observer import CacheObserver


@pytest.mark.unit
@pytest.mark.observer
class TestMapState:    
  def test_initialization(self, mock_map_state):
    assert mock_map_state is not None
    assert len(mock_map_state._observers) == 0
    assert mock_map_state._notifications_enabled is True
  
  def test_attach_observer(self, mock_map_state):
    observer = Mock(spec=Observer)
    
    mock_map_state.attach(observer)
    
    assert observer in mock_map_state._observers
    assert len(mock_map_state._observers) == 1
  
  def test_attach_same_observer_twice(self, mock_map_state):
    observer = Mock(spec=Observer)
    
    mock_map_state.attach(observer)
    mock_map_state.attach(observer)
    
    assert len(mock_map_state._observers) == 1
  
  def test_detach_observer(self, mock_map_state):
    observer = Mock(spec=Observer)
    
    mock_map_state.attach(observer)
    mock_map_state.detach(observer)
    
    assert observer not in mock_map_state._observers
    assert len(mock_map_state._observers) == 0
  
  def test_notify_observers(self, mock_map_state, mock_quality_strategy):
    observer = Mock(spec=Observer)
    mock_map_state.attach(observer)
    
    mock_map_state.set_strategy(mock_quality_strategy)
    
    observer.update.assert_called_once()
    call_args = observer.update.call_args
    
    assert call_args[0][0] == mock_map_state
    assert call_args[0][1] == 'strategy'
  
  def test_disable_notifications(self, mock_map_state):
    observer = Mock(spec=Observer)
    mock_map_state.attach(observer)
    
    mock_map_state.disable_notifications()
    mock_map_state.notify('test')
    
    observer.update.assert_not_called()
  
  def test_enable_notifications(self, mock_map_state):
    observer = Mock(spec=Observer)
    mock_map_state.attach(observer)
    
    mock_map_state.disable_notifications()
    mock_map_state.enable_notifications()
    mock_map_state.notify('test')
    
    observer.update.assert_called_once()
  
  def test_set_strategy(self, mock_map_state, mock_quality_strategy):
    observer = Mock(spec=Observer)
    mock_map_state.attach(observer)
    
    mock_map_state.set_strategy(mock_quality_strategy)
    
    assert mock_map_state.current_strategy == mock_quality_strategy
    observer.update.assert_called_once()
  
  def test_set_active_layers(self, mock_map_state):
    observer = Mock(spec=Observer)
    mock_map_state.attach(observer)
    
    layers = {'layer1', 'layer2'}
    mock_map_state.set_active_layers(layers)
    
    assert mock_map_state.active_layers == layers
    observer.update.assert_called_once()
  
  def test_toggle_layer(self, mock_map_state):
    observer = Mock(spec=Observer)
    mock_map_state.attach(observer)
    
    mock_map_state.toggle_layer('test_layer')
    assert 'test_layer' in mock_map_state.active_layers
    
    mock_map_state.toggle_layer('test_layer')
    assert 'test_layer' not in mock_map_state.active_layers
    
    assert observer.update.call_count == 2
  
  def test_set_viewport_bounds(self, mock_map_state):
    observer = Mock(spec=Observer)
    mock_map_state.attach(observer)
    
    bounds = {
        'north': 1.0,
        'south': -1.0,
        'east': 1.0,
        'west': -1.0
    }
    
    mock_map_state.set_viewport_bounds(bounds)
    
    assert mock_map_state.viewport_bounds == bounds
    observer.update.assert_called_once()
  
  def test_set_param(self, mock_map_state):
    observer = Mock(spec=Observer)
    mock_map_state.attach(observer)
    
    mock_map_state.set_param('test_key', 'test_value')
    
    assert mock_map_state.get_param('test_key') == 'test_value'
    observer.update.assert_called_once()
  
  def test_get_state_summary(self, mock_map_state, mock_quality_strategy):
    mock_map_state.set_strategy(mock_quality_strategy)
    mock_map_state.set_active_layers({'layer1'})
    
    summary = mock_map_state.get_state_summary()
    
    assert 'strategy' in summary
    assert 'active_layers' in summary
    assert 'num_observers' in summary
    assert summary['strategy'] == mock_quality_strategy.get_name()
  
  def test_reset(self, mock_map_state, mock_quality_strategy):
    observer = Mock(spec=Observer)
    mock_map_state.attach(observer)
    
    mock_map_state.set_strategy(mock_quality_strategy)
    mock_map_state.set_active_layers({'layer1'})
    mock_map_state.set_param('key', 'value')
    
    mock_map_state.reset()
    
    assert mock_map_state.current_strategy is None
    assert len(mock_map_state.active_layers) == 0
    assert mock_map_state.get_param('key') is None


@pytest.mark.unit
@pytest.mark.observer
class TestRecommendationObserver:
  def test_initialization(self):
    mock_analyzer = Mock()
    observer = RecommendationObserver(mock_analyzer)
    
    assert observer.analyzer == mock_analyzer
    assert observer.current_scores is None
  
  def test_update_with_strategy_change(self, mock_map_state, mock_quality_strategy, mock_scores_df):
    mock_analyzer = Mock()
    mock_analyzer.metrics_df = mock_scores_df
    
    observer = RecommendationObserver(mock_analyzer)
    
    observer.update(
      mock_map_state,
      'strategy',
      new_strategy=mock_quality_strategy
    )
    
    assert observer.current_scores is not None
    assert 'score' in observer.current_scores.columns
    assert 'rank' in observer.current_scores.columns
  
  def test_update_ignore_other_changes(self, mock_map_state):
    mock_analyzer = Mock()
    observer = RecommendationObserver(mock_analyzer)
    
    observer.update(mock_map_state, 'viewport')
    
    assert observer.current_scores is None
  
  def test_get_scores_df(self, mock_map_state, mock_quality_strategy, mock_scores_df):
    mock_analyzer = Mock()
    mock_analyzer.metrics_df = mock_scores_df
    
    observer = RecommendationObserver(mock_analyzer)
    observer.update(mock_map_state, 'strategy', new_strategy=mock_quality_strategy)
    
    scores = observer.get_scores_df()
    
    assert scores is not None
    assert len(scores) > 0
  
  def test_get_top_districts(self, mock_map_state, mock_quality_strategy, mock_scores_df):
    mock_analyzer = Mock()
    mock_analyzer.metrics_df = mock_scores_df
    
    observer = RecommendationObserver(mock_analyzer)
    observer.update(mock_map_state, 'strategy', new_strategy=mock_quality_strategy)
    
    top3 = observer.get_top_districts(3)
    
    assert top3 is not None
    assert len(top3) <= 3
  
  def test_get_district_score(self, mock_map_state, mock_quality_strategy, mock_scores_df):
    mock_analyzer = Mock()
    mock_analyzer.metrics_df = mock_scores_df
    
    observer = RecommendationObserver(mock_analyzer)
    observer.update(mock_map_state, 'strategy', new_strategy=mock_quality_strategy)
    
    district_name = mock_scores_df.iloc[0]['district_name']
    details = observer.get_district_score(district_name)
    
    assert details is not None
    assert 'score' in details
    assert 'rank' in details
    assert 'metrics' in details


@pytest.mark.unit
@pytest.mark.observer
class TestCacheObserver:    
  def test_initialization(self):
    mock_analyzer = Mock()
    observer = CacheObserver(mock_analyzer)
    
    assert observer.analyzer == mock_analyzer
    assert observer.cache_valid is True
  
  def test_invalidate_on_layers_change(self, mock_map_state):
    mock_analyzer = Mock()
    observer = CacheObserver(mock_analyzer)
    
    observer.update(
      mock_map_state,
      'layers',
      added={'crimes'},
      removed=set()
    )
    
    mock_analyzer.invalidate_cache.assert_called_once()
    assert observer.cache_valid is False
  
  def test_no_invalidate_on_visual_layers(self, mock_map_state):
    mock_analyzer = Mock()
    observer = CacheObserver(mock_analyzer)
    
    observer.update(
      mock_map_state,
      'layers',
      added={'districts'},
      removed=set()
    )
    
    mock_analyzer.invalidate_cache.assert_not_called()
    assert observer.cache_valid is True
  
  def test_invalidate_on_reset(self, mock_map_state):
    mock_analyzer = Mock()
    observer = CacheObserver(mock_analyzer)
    
    observer.update(mock_map_state, 'reset')
    
    mock_analyzer.invalidate_cache.assert_called_once()
    assert observer.cache_valid is False
  
  def test_is_cache_valid(self):
    mock_analyzer = Mock()
    observer = CacheObserver(mock_analyzer)
    
    assert observer.is_cache_valid() is True
    
    observer.cache_valid = False
    assert observer.is_cache_valid() is False
  
  def test_mark_cache_valid(self):
    mock_analyzer = Mock()
    observer = CacheObserver(mock_analyzer)
    
    observer.cache_valid = False
    observer.mark_cache_valid()
    
    assert observer.cache_valid is True