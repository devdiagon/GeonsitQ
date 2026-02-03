from platform import system
import pytest
from unittest.mock import patch

from integration.backend_facade import RecommendationSystem


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndFlows:
    
  @pytest.fixture
  def system(self, test_config_path, mock_city_graph):
    with patch('integration.backend_facade.CityGraph', return_value=mock_city_graph):
      return RecommendationSystem(config_path=str(test_config_path))
    
  def test_complete_recommendation_flow(self, system, mock_districts_gdf):
    # 1. Seleccionar estrategia
    success = system.set_strategy('quality_of_life')
    assert success is True
    
    # 2. Obtener top distritos
    top_districts = system.get_top_districts(3)
    assert top_districts is not None
    assert len(top_districts) <= 3
    
    # 3. Obtener detalles del mejor distrito
    best_district_name = top_districts.iloc[0]['district_name']
    details = system.get_district_details(best_district_name)
    
    assert details is not None
    assert details['score'] == top_districts.iloc[0]['score']
    assert details['rank'] == 1
    
    # 4. Verificar métricas
    assert 'safety' in details['metrics']
    assert 'transport' in details['metrics']
    
  def test_compare_strategies_flow(self, system):
    strategies = ['quality_of_life', 'tourist', 'convenience']
    results = {}
    
    for strategy_name in strategies:
      system.set_strategy(strategy_name)
      
      top = system.get_top_districts(1)
      results[strategy_name] = {
        'district': top.iloc[0]['district_name'],
        'score': top.iloc[0]['score']
      }
    
    assert len(results) == 3
    
    scores = [r['score'] for r in results.values()]
    assert len(set(scores)) >= 1
    
  def test_cache_workflow(self, system):
    system.set_strategy('quality_of_life')
    scores_1 = system.get_scores_df()
    
    cache_info = system.analyzer.get_cache_info()
    assert cache_info['exists'] is True, "Caché debería existir después del primer análisis"
    
    scores_2 = system.get_scores_df()
    
    import pandas as pd
    pd.testing.assert_frame_equal(
      scores_1[['district_name', 'score', 'rank']],
      scores_2[['district_name', 'score', 'rank']],
      check_dtype=False
    )
    
    system.invalidate_cache()
    
    cache_info_after = system.analyzer.get_cache_info()
    assert cache_info_after['exists'] is False, "Caché debería estar invalidado"
    
    system.analyzer.analyze_all_districts(force_refresh=True)
    scores_3 = system.get_scores_df()
    
    cache_info_final = system.analyzer.get_cache_info()
    assert cache_info_final['exists'] is True, "Caché debería recrearse"
    
    pd.testing.assert_frame_equal(
      scores_1[['district_name', 'score']],
      scores_3[['district_name', 'score']],
      check_dtype=False
    )
    
  def test_full_analysis_pipeline(self, system):
    # 1. Obtener métricas base
    metrics = system.get_metrics_df()
    assert metrics is not None
    
    # 2. Aplicar estrategia
    system.set_strategy('tourist')
    
    # 3. Obtener scores
    scores = system.get_scores_df()
    assert 'score' in scores.columns
    
    # 4. Verificar que scores están calculados correctamente        
    metrics_sorted = metrics.sort_values('services', ascending=False)
    top_services_district = metrics_sorted.iloc[0]['district_name']
    
    district_score = scores[scores['district_name'] == top_services_district].iloc[0]['score']
    
    assert district_score > scores['score'].median()
    
  def test_observer_integration(self, system):
    assert len(system.map_state._observers) == 2
    
    system.set_strategy('convenience')
    
    scores = system.rec_observer.get_scores_df()
    assert scores is not None
    assert len(scores) > 0


@pytest.mark.integration
class TestErrorHandling:
    
  @pytest.fixture
  def system(self, test_config_path, mock_districts_gdf):
    from unittest.mock import Mock
    
    mock_city = Mock()
    mock_city.get_graph.return_value = mock_districts_gdf
    mock_city.get_parks.return_value = None  # Sin parques
    mock_city.get_tourist_places.return_value = None  # Sin lugares turísticos
    mock_city.get_places.return_value = mock_districts_gdf['display_name'].tolist()
    
    with patch('integration.backend_facade.CityGraph', return_value=mock_city):
      return RecommendationSystem(config_path=str(test_config_path))
    
  def test_analysis_with_missing_data(self, system):
    system.set_strategy('quality_of_life')
    scores = system.get_scores_df()
    
    assert scores is not None
    assert 'green' in scores.columns
    assert 'services' in scores.columns
    
  def test_invalid_district_name(self, system):
    system.set_strategy('tourist')
    
    details = system.get_district_details('Distrito Inexistente XYZ')
    
    assert details is None