import pytest
import numpy as np

from analyzers.normalizer import (
  normalize_min_max,
  normalize_z_score,
  safe_normalize,
  invert_scale,
  normalize_with_weights,
  handle_missing_values,
  robust_normalize
)


@pytest.mark.unit
class TestNormalizeMinMax:    
  def test_normalize_basic(self):
    values = [1, 2, 3, 4, 5]
    normalized = normalize_min_max(values)
    
    assert len(normalized) == len(values)
    assert normalized.min() == 0.0
    assert normalized.max() == 1.0
    assert np.allclose(normalized, [0.0, 0.25, 0.5, 0.75, 1.0])
    
  def test_normalize_with_range(self):
    values = [0, 50, 100]
    normalized = normalize_min_max(values, feature_range=(0, 10))
    
    assert normalized.min() == 0.0
    assert normalized.max() == 10.0
    assert normalized[1] == 5.0
    
  def test_normalize_constant_values(self):
    values = [5, 5, 5, 5]
    normalized = normalize_min_max(values)
    
    assert np.allclose(normalized, [0.5, 0.5, 0.5, 0.5])
    
  def test_normalize_single_value(self):
    values = [42]
    normalized = normalize_min_max(values)
    
    assert len(normalized) == 1
    assert normalized[0] == 0.5
    
  def test_normalize_negative_values(self):
    values = [-10, -5, 0, 5, 10]
    normalized = normalize_min_max(values)
    
    assert normalized.min() == 0.0
    assert normalized.max() == 1.0


@pytest.mark.unit
class TestNormalizeZScore:    
  def test_z_score_basic(self):
    values = [1, 2, 3, 4, 5]
    z_scores = normalize_z_score(values)

    assert len(z_scores) == len(values)

    assert np.abs(z_scores.mean()) < 0.0001

    assert np.abs(z_scores.std() - 1.0) < 0.0001
    
  def test_z_score_with_clipping(self):
    values = [1, 2, 3, 4, 100]
    z_scores = normalize_z_score(values, clip_std=2.0)
      
    assert z_scores.max() <= 2.0
    assert z_scores.min() >= -2.0
    
  def test_z_score_constant_values(self):
    values = [7, 7, 7, 7]
    z_scores = normalize_z_score(values)
      
    assert np.allclose(z_scores, [0, 0, 0, 0])


@pytest.mark.unit
class TestSafeNormalize:    
  def test_safe_normalize_basic(self):
    result = safe_normalize(75, 0, 100)
    assert result == 0.75
    
  def test_safe_normalize_equal_bounds(self):
    result = safe_normalize(50, 50, 50)
    assert result == 0.5
    
  def test_safe_normalize_with_nan(self):
    result = safe_normalize(np.nan, 0, 100)
    assert result == 0.5
    
  def test_safe_normalize_clipping(self):
    result_high = safe_normalize(150, 0, 100)
    result_low = safe_normalize(-50, 0, 100)
      
    assert result_high == 1.0
    assert result_low == 0.0


@pytest.mark.unit
class TestInvertScale:    
  def test_invert_scale_basic(self):
    values = [0.0, 0.25, 0.5, 0.75, 1.0]
    inverted = invert_scale(values)
    
    expected = [1.0, 0.75, 0.5, 0.25, 0.0]
    assert np.allclose(inverted, expected)
    
  def test_invert_scale_custom_range(self):
    values = [0, 5, 10]
    inverted = invert_scale(values, scale_range=(0, 10))
    
    expected = [10, 5, 0]
    assert np.allclose(inverted, expected)
    
  def test_invert_scale_symmetry(self):
    values = [0.2, 0.5, 0.8]
    double_inverted = invert_scale(invert_scale(values))
      
    assert np.allclose(double_inverted, values)


@pytest.mark.unit
class TestNormalizeWithWeights:    
  def test_normalize_with_weights_min_max(self):
    metrics_dict = {
      'safety': [0.3, 0.7, 0.9],
      'transport': [0.5, 0.6, 0.8]
    }
    weights = {
      'safety': 0.6,
      'transport': 0.4
    }
      
    result = normalize_with_weights(metrics_dict, weights, method='min_max')
      
    assert 'safety' in result
    assert 'transport' in result
    assert len(result['safety']) == 3
    
  def test_normalize_with_weights_z_score(self):
    metrics_dict = {
      'metric1': [1, 2, 3, 4, 5]
    }
    weights = {'metric1': 1.0}
    
    result = normalize_with_weights(metrics_dict, weights, method='z_score')
    
    assert 'metric1' in result
    
  def test_normalize_with_weights_missing_weight(self):
    metrics_dict = {
      'metric1': [1, 2, 3],
      'metric2': [4, 5, 6]
    }
    weights = {
      'metric1': 1.0
    }
    
    result = normalize_with_weights(metrics_dict, weights)
    
    assert 'metric1' in result
    assert 'metric2' not in result


@pytest.mark.unit
class TestHandleMissingValues:    
  def test_handle_missing_neutral(self):
    values = [0.3, np.nan, 0.7, 0.9]
    result = handle_missing_values(values, strategy='neutral')
    
    assert not np.any(np.isnan(result))
    assert result[1] == 0.5
    
  def test_handle_missing_zero(self):
    values = [0.3, np.nan, 0.7]
    result = handle_missing_values(values, strategy='zero')
    
    assert result[1] == 0.0
  
  def test_handle_missing_mean(self):
    values = [0.2, np.nan, 0.8]
    result = handle_missing_values(values, strategy='mean')
    
    assert result[1] == 0.5
  
  def test_handle_missing_median(self):
    values = [0.1, 0.5, np.nan, 0.9]
    result = handle_missing_values(values, strategy='median')
    
    assert result[2] == 0.5
  
  def test_handle_missing_all_nan(self):
    values = [np.nan, np.nan, np.nan]
    result = handle_missing_values(values, strategy='mean')
    
    assert not np.any(np.isnan(result))


@pytest.mark.unit
class TestRobustNormalize:    
  def test_robust_normalize_basic(self):
    values = [1, 2, 3, 4, 5]
    normalized = robust_normalize(values)
    
    assert len(normalized) == len(values)
    assert 0.0 <= normalized.min() <= 1.0
    assert 0.0 <= normalized.max() <= 1.0
    
  def test_robust_normalize_with_outliers(self):
    values = [1, 2, 3, 4, 5, 100]
    normalized = robust_normalize(values, percentile_range=(10, 90))
    
    assert normalized[-1] == 1.0
    
  def test_robust_normalize_constant(self):
    values = [5, 5, 5, 5]
    normalized = robust_normalize(values)
    
    assert np.allclose(normalized, [0.5, 0.5, 0.5, 0.5])