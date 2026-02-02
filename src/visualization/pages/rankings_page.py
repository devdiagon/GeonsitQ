import streamlit as st


def render_rankings_page():
  st.markdown("### Rankings y Estadísticas")
    
  # Validaciones
  if st.session_state.current_strategy is None:
    st.warning("Por favor, selecciona una estrategia en el sidebar")
    return
  
  # Gráfico de barras - Top N
  _render_ranking_chart()
  
  # Tabla interactiva
  _render_interactive_table()


def _render_ranking_chart():
  scores_df = st.session_state.system.get_scores_df()
  strategy = st.session_state.system.get_current_strategy()
    
  if scores_df is None:
    st.error("No hay datos disponibles")
    return
    
  # Gráfico de barras - Top N
  st.markdown(f"#### Top {st.session_state.top_n} Distritos")
  
  fig_ranking = st.session_state.chart_generator.create_ranking_bar_chart(
    scores_df=scores_df,
    strategy=strategy,
    top_n=st.session_state.top_n
  )
    
  st.plotly_chart(fig_ranking, width='stretch')
    
  # Dos columnas para gráficos adicionales
  col1, col2 = st.columns(2)
    
  with col1:
    st.markdown("#### Distribución de Scores")
    fig_dist = st.session_state.chart_generator.create_score_distribution(
      scores_df=scores_df,
      strategy=strategy
    )
    st.plotly_chart(fig_dist, width='stretch')
  
  with col2:
    st.markdown("#### Correlación entre Métricas")
    fig_corr = st.session_state.chart_generator.create_correlation_heatmap(
      scores_df=scores_df
    )
    st.plotly_chart(fig_corr, width='stretch')
  
  # Tabla comparativa
  st.markdown("---")


def _render_interactive_table():
  st.markdown("#### Tabla Comparativa Detallada")
    
  top_districts = st.session_state.system.get_top_districts(st.session_state.top_n)
    
  fig_table = st.session_state.chart_generator.create_comparison_table(
    top_districts=top_districts
  )
    
  st.plotly_chart(fig_table, width='stretch')
