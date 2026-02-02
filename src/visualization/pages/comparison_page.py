import streamlit as st


def render_comparison_page():
  st.markdown("### Comparación Detallada")
  
  if st.session_state.current_strategy is None:
    st.warning("Por favor, selecciona una estrategia en el sidebar")
    return
  
  # Verificar modo de comparación
  if st.session_state.comparison_mode == 'multi_strategy':
    render_multi_strategy_comparison()
  else:
    render_individual_comparison()


def render_individual_comparison():
  scores_df = st.session_state.system.get_scores_df()
  strategy = st.session_state.system.get_current_strategy()
    
  if scores_df is None:
    st.error("No hay datos disponibles")
    return
    
  # Selector de distritos para comparar
  st.markdown("#### Selecciona Distritos para Comparar")
    
  all_districts = scores_df['district_name'].tolist()
    
  # Por defecto, seleccionar top 3
  col1, col2, col3 = st.columns(3)

  with col1:
    if st.button("Top 3", width='stretch'):
      st.session_state.selected_districts_comparison = all_districts[:3]
      st.session_state.multiselect_districts = all_districts[:3]
      st.rerun()
    
  with col2:
    if st.button("Top 5", width='stretch'):
      st.session_state.selected_districts_comparison = all_districts[:5]
      st.session_state.multiselect_districts = all_districts[:5]
      st.rerun()
    
  with col3:
    if st.button("Aleatorio", width='stretch'):
      import random
      rng_num = min(3, len(all_districts))
      random_selection = random.sample(all_districts, rng_num)
      st.session_state.selected_districts_comparison = random_selection
      st.session_state.multiselect_districts = random_selection
      st.rerun()

  selected_districts = st.multiselect(
    "Distritos:",
    options=all_districts,
    max_selections=5,
    key='multiselect_districts',
    help="Selecciona hasta 5 distritos para comparar",
  )

  if selected_districts != st.session_state.selected_districts_comparison:
    st.session_state.selected_districts_comparison = selected_districts
    
  if len(selected_districts) == 0:
    st.info("Selecciona al menos un distrito para ver la comparación")
    return
  
  st.markdown(f"**Comparando {len(selected_districts)} distrito(s)**")

  st.markdown("#### Comparación de Métricas")
    
  fig_comparison = st.session_state.chart_generator.create_metrics_comparison_chart(
    scores_df=scores_df,
    district_names=selected_districts,
    strategy=strategy
  )
    
  st.plotly_chart(fig_comparison, width='stretch')
    
  # Radar charts individuales
  st.markdown("---")

  st.markdown("#### Análisis Individual")
    
  # Crear tabs para cada distrito
  district_tabs = st.tabs([f"{name[:20]}" for name in selected_districts])
    
  for i, district_name in enumerate(selected_districts):
    with district_tabs[i]:
      district_data = scores_df[scores_df['district_name'] == district_name].iloc[0]
      
      # Información del distrito
      col1, col2, col3, col4 = st.columns(4)
      
      with col1:
        st.metric("Score", f"{district_data['score']:.3f}")
      with col2:
        st.metric("Ranking", f"#{int(district_data['rank'])}")
      with col3:
        st.metric("Seguridad", f"{district_data['safety']:.2f}")
      with col4:
        st.metric("Transporte", f"{district_data['transport']:.2f}")
      
      # Radar chart
      fig_radar = st.session_state.chart_generator.create_metrics_radar_chart(
        district_data=district_data,
        strategy=strategy
      )
      
      st.plotly_chart(fig_radar, width='stretch')
      
      # Detalles adicionales
      with st.expander("Ver detalles completos"):
        details = st.session_state.system.get_district_details(district_name)
        if details:
          st.json(details)


def render_multi_strategy_comparison():
  st.markdown("#### Análisis Multi-Estrategia")
  st.info("Comparando resultados de todas las estrategias disponibles")
    
  # Obtener scores de todas las estrategias
  all_scores = get_all_strategy_scores()
    
  # Selector de distrito para analizar
  first_strategy_scores = list(all_scores.values())[0]
  all_districts = first_strategy_scores['district_name'].tolist()
    
  selected_district = st.selectbox(
    "Selecciona un distrito para analizar:",
    options=all_districts,
    index=0,
    key='select_multi_strategy_district'
  )
    
  # Gráfico de comparación multi-estrategia
  fig_multi = st.session_state.chart_generator.create_multi_strategy_comparison(
    all_scores=all_scores,
    district_name=selected_district
  )
    
  st.plotly_chart(fig_multi, width='stretch')
    
  # Tabla comparativa
  st.markdown("#### Scores Detallados por Estrategia")
    
  comparison_data = []
  for strategy_name, scores_df in all_scores.items():
    district_data = scores_df[scores_df['district_name'] == selected_district]
    if len(district_data) > 0:
      row = district_data.iloc[0]
      comparison_data.append({
        'Estrategia': strategy_name,
        'Score': f"{row['score']:.3f}",
        'Ranking': f"#{int(row['rank'])}",
        'Seguridad': f"{row['safety']:.2f}",
        'Transporte': f"{row['transport']:.2f}",
        'Verde': f"{row['green']:.2f}",
        'Servicios': f"{row['services']:.2f}"
      })
    
  import pandas as pd
  df_comparison = pd.DataFrame(comparison_data)
  st.dataframe(df_comparison, width='stretch', hide_index=True)


def get_all_strategy_scores():    
    if 'all_strategy_scores' not in st.session_state:
      st.session_state.all_strategy_scores = {}
    
    strategies = st.session_state.system.get_available_strategies()
    current_strategy = st.session_state.current_strategy
    
    # Calcular scores para cada estrategia
    for strategy_name in strategies.keys():
      if strategy_name not in st.session_state.all_strategy_scores:
        with st.spinner(f'Calculando scores para {strategy_name}...'):
          st.session_state.system.set_strategy(strategy_name)
          st.session_state.all_strategy_scores[strategy_name] = st.session_state.system.get_scores_df()
    
    # Restaurar estrategia actual
    st.session_state.system.set_strategy(current_strategy)
    
    return st.session_state.all_strategy_scores
