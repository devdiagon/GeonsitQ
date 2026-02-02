import streamlit as st


def render_map_page():
  st.markdown("### Mapa de Distritos por Score")
    
  # Validaciones
  if st.session_state.current_strategy is None:
    st.warning("Por favor, selecciona una estrategia en el sidebar")
    return
    
  # Generar y mostrar mapa
  _render_map()


def _render_map():
  # Obtener datos
  scores_df = st.session_state.system.get_scores_df()
  districts_gdf = st.session_state.system.city.get_graph()
  strategy = st.session_state.system.get_current_strategy()
  
  if scores_df is None or len(scores_df) == 0:
    st.error("No hay datos de scores disponibles")
    return
  
  # Crear mapa
  with st.spinner('Generando mapa...'):
    m = st.session_state.map_renderer.create_base_map()
      
    m = st.session_state.map_renderer.render_districts_choropleth(
      m=m,
      districts_gdf=districts_gdf,
      scores_df=scores_df,
      strategy=strategy,
      show_labels=st.session_state.show_labels,
      layer_name=f"Scores - {strategy.get_name()}"
    )
      
    # ========== AGREGAR CAPAS ADICIONALES ==========
    m = st.session_state.map_renderer.add_city_layers(
      m=m,
      city_graph=st.session_state.system.city,
      layers_config=st.session_state.map_layers_config
    )
    
    # Agregar controles
    m = st.session_state.map_renderer.add_fullscreen_control(m)
    m = st.session_state.map_renderer.add_minimap(m)
    
    import folium
    folium.LayerControl(position='topright', collapsed=False).add_to(m)

  # Mostrar mapa
  from streamlit_folium import st_folium
  
  st_folium(
    m,
    width=None,
    height=600,
    returned_objects=[]
  )
  
  # Información adicional
  st.markdown("---")
  
  col1, col2, col3 = st.columns(3)
    
  with col1:
    avg_score = scores_df['score'].mean()
    st.metric("Score Promedio", f"{avg_score:.3f}")
  
  with col2:
    max_score = scores_df['score'].max()
    st.metric("Score Máximo", f"{max_score:.3f}")
  
  with col3:
    min_score = scores_df['score'].min()
    st.metric("Score Mínimo", f"{min_score:.3f}")
