import streamlit as st


def on_strategy_change():    
  # Actualizar estrategia
  st.session_state.current_strategy = st.session_state.temp_strategy
  
  # Aplicar cambio en el backend
  with st.spinner('Actualizando análisis...'):
    st.session_state.system.set_strategy(st.session_state.current_strategy)


def on_visualization_option_change():
  st.session_state.force_map_update = True


def render_sidebar():
  # 1. Selector de estrategia
  _render_strategy_selector()
  
  # 2. Opciones de visualización
  _render_visualization_options()
  
  # 3. Capas del mapa
  _render_map_layers()
  
  # 4. Estado del sistema
  _render_system_status()
  
  # 5. Acciones
  _render_actions()


def _render_strategy_selector():
  st.sidebar.markdown("## Configuración")
    
  # Selector de estrategia
  st.sidebar.markdown("### Estrategia de Análisis")
  
  strategies = st.session_state.system.get_available_strategies()
  strategy_names = list(strategies.keys())
  
  # Mapeo de nombres técnicos a nombres amigables
  strategy_display_names = {
    'quality_of_life': 'Calidad de Vida',
    'tourist': 'Turista/Visitante',
    'convenience': 'Servicios y Conveniencia'
  }
    
  # Crear lista de opciones para el radio
  options = [strategy_display_names.get(name, name) for name in strategy_names]

  # Obtener índice actual
  current_index = strategy_names.index(st.session_state.current_strategy)
    
  # Radio button para seleccionar estrategia
  selected_display = st.sidebar.radio(
    "Selecciona tu perfil:",
    options,
    index=current_index,
    key='temp_strategy_display',
    help="Cada estrategia prioriza diferentes aspectos de los distritos"
  )
    
  # Obtener nombre técnico de la estrategia seleccionada
  selected_strategy = strategy_names[options.index(selected_display)]
  
  # Actualizar estrategia si cambió
  if selected_strategy != st.session_state.current_strategy:
    st.session_state.temp_strategy = selected_strategy
    on_strategy_change()
    st.rerun()
    
  # Mostrar descripción de la estrategia
  if st.session_state.current_strategy:
    strategy_obj = st.session_state.system.get_current_strategy()
    st.sidebar.info(f"**{strategy_obj.get_description()}**")
    
    # Mostrar pesos
    with st.sidebar.expander("Ver pesos de métricas", expanded=False):
      weights = strategy_obj.get_weights()
      for metric, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        if weight > 0:
          col1, col2 = st.columns([3, 1])
          with col1:
            st.progress(weight, text=f"**{metric.capitalize()}**")
          with col2:
            st.write(f"{weight*100:.0f}%")
  
  st.sidebar.markdown("---")


def _render_visualization_options():
  st.sidebar.markdown("### Opciones de Visualización")
    
  new_show_labels = st.sidebar.checkbox(
    "Mostrar nombres en mapa",
    value=st.session_state.show_labels,
    key='checkbox_labels',
    help="Muestra etiquetas con nombres de distritos en el mapa"
  )

  if new_show_labels != st.session_state.show_labels:
    st.session_state.show_labels = new_show_labels
    on_visualization_option_change()
    
  new_top_n = st.sidebar.slider(
    "Top N distritos a mostrar",
    min_value=5,
    max_value=20,
    value=st.session_state.top_n,
    step=1,
    key='slider_top_n',
    help="Número de distritos en rankings y gráficos"
  )

  if new_top_n != st.session_state.top_n:
    st.session_state.top_n = new_top_n
    
  # Modo de comparación
  st.sidebar.markdown("### Modo de Análisis")
    
  comparison_options = {
    'individual': 'Individual',
    'multi_strategy': 'Multi-estrategia'
  }
    
  st.session_state.comparison_mode = st.sidebar.radio(
    "Tipo de análisis:",
    options=list(comparison_options.keys()),
    format_func=lambda x: comparison_options[x],
    index=0 if st.session_state.comparison_mode == 'individual' else 1,
    help="Individual: analiza con la estrategia seleccionada\nMulti-estrategia: compara resultados de todas las estrategias"
  )

  st.sidebar.markdown("---")


def _render_map_layers():
  st.sidebar.markdown("### Capas del Mapa")
  st.sidebar.caption("Selecciona qué capas mostrar en el mapa (solo visual)")
    
  # Inicializar configuración de capas si no existe
  if 'map_layers_config' not in st.session_state:
    st.session_state.map_layers_config = {
      'parks': False,
      'tourist_places': False,
      'crimes': False,
      'metro': False,
      'bus_routes': False,
      'bus_stops': False
    }
    
  # Checkboxes para cada capa
  new_layers_config = {}
    
  with st.sidebar.expander("Capas de Ciudad", expanded=False):
    new_layers_config['parks'] = st.checkbox(
      "Parques",
      value=st.session_state.map_layers_config['parks'],
      key='checkbox_layer_parks',
      help="Muestra parques públicos en el mapa"
    )
        
    new_layers_config['tourist_places'] = st.checkbox(
      "Lugares Turísticos",
      value=st.session_state.map_layers_config['tourist_places'],
      key='checkbox_layer_tourist',
      help="Muestra museos, galerías y atracciones"
    )
        
    new_layers_config['crimes'] = st.checkbox(
      "Zonas de Criminalidad",
      value=st.session_state.map_layers_config['crimes'],
      key='checkbox_layer_crimes',
      help="Muestra zonas por nivel de criminalidad"
    )
    
  with st.sidebar.expander("Capas de Transporte", expanded=False):
    new_layers_config['metro'] = st.checkbox(
      "Metro",
      value=st.session_state.map_layers_config['metro'],
      key='checkbox_layer_metro',
      help="Muestra línea y estaciones del metro"
    )
    
    new_layers_config['bus_routes'] = st.checkbox(
      "Rutas de Buses",
      value=st.session_state.map_layers_config['bus_routes'],
      key='checkbox_layer_bus_routes',
      help="Muestra hasta 50 rutas de buses principales"
    )
    
    new_layers_config['bus_stops'] = st.checkbox(
      "Paradas de Bus",
      value=st.session_state.map_layers_config['bus_stops'],
      key='checkbox_layer_bus_stops',
      help="Muestra paradas de buses urbanos"
    )
    
  # Detectar cambios en las capas
  if new_layers_config != st.session_state.map_layers_config:
    st.session_state.map_layers_config = new_layers_config
  
  st.sidebar.markdown("---")


def _render_system_status():
  st.sidebar.markdown("### Estado del Sistema")
    
  status = st.session_state.system.get_system_status()
  
  col1, col2 = st.sidebar.columns(2)

  with col1:
    st.metric("Distritos", status['num_districts'])
  with col2:
    st.metric("Estrategias", len(status['available_strategies']))
  
  st.sidebar.markdown("---")


def _render_actions():
  st.sidebar.markdown("### Acciones")
    
  col1, col2 = st.sidebar.columns(2)
  
  with col1:
    if st.button("Refresh", width='stretch', help="Recalcula métricas (ignora caché)"):
      with st.spinner('Recalculando...'):
        st.session_state.system.refresh_analysis()
        st.rerun()
  
  with col2:
    if st.button("Limpiar", width='stretch', help="Invalida caché"):
      st.session_state.system.invalidate_cache()
      st.rerun()
