import pytest
from strategies.base_strategy import BaseStrategy
from strategies.qol_strategy import QualityOfLifeStrategy
from strategies.tourist_strategy import TouristStrategy
from strategies.convenience_strategy import ConvenienceStrategy
from strategies.strategy_factory import StrategyFactory


@pytest.mark.unit
@pytest.mark.strategy
class TestBaseStrategy:    
  def test_abstract_methods(self):
    with pytest.raises(TypeError):
      BaseStrategy()


@pytest.mark.unit
@pytest.mark.strategy
class TestQualityOfLifeStrategy:
    
  def test_initialization(self, mock_quality_strategy):
    assert mock_quality_strategy is not None
    assert mock_quality_strategy.get_name() == "Calidad de Vida"
  
  def test_weights_sum(self, mock_quality_strategy):
    weights = mock_quality_strategy.get_weights()
    total = sum(w for w in weights.values() if w > 0)
    assert 0.99 <= total <= 1.01
  
  def test_calculate_score(self, mock_quality_strategy):
    metrics = {
      'safety': 0.8,
      'transport': 0.7,
      'green': 0.6,
      'services': 0.5
    }
    
    score = mock_quality_strategy.calculate_final_score(metrics)
    assert 0.0 <= score <= 1.0
    
  def test_penalties(self, mock_quality_strategy):
    metrics_unsafe = {
      'safety': 0.2,
      'transport': 0.8,
      'green': 0.7,
      'services': 0.6
    }
    
    metrics_safe = {
      'safety': 0.9,
      'transport': 0.8,
      'green': 0.7,
      'services': 0.6
    }
    
    score_unsafe = mock_quality_strategy.calculate_final_score(metrics_unsafe)
    score_safe = mock_quality_strategy.calculate_final_score(metrics_safe)
    
    assert score_safe > score_unsafe


@pytest.mark.unit
@pytest.mark.strategy
class TestStrategyFactory:
  def test_create_strategy_by_name(self):
    strategy = StrategyFactory.create_strategy('quality_of_life')
    assert isinstance(strategy, QualityOfLifeStrategy)
    
  def test_create_invalid_strategy(self):
    with pytest.raises(ValueError):
      StrategyFactory.create_strategy('invalid_strategy')
    
  def test_create_all_strategies(self, all_strategies):
    assert len(all_strategies) == 3
    assert 'quality_of_life' in all_strategies
    assert 'tourist' in all_strategies
    assert 'convenience' in all_strategies