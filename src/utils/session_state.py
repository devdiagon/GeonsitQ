import streamlit as st
from datetime import datetime

# Imports
from integration.backend_facade import RecommendationSystem
from visualization.map_renderer import MapRenderer
from visualization.chart_generator import ChartGenerator


def init_session_state():
  # Backend system
  if 'system' not in st.session_state:
    with st.spinner('Inicializando sistema...'):
      st.session_state.system = RecommendationSystem(config_path='config.yaml')
      st.session_state.init_time = datetime.now()
  
  # Renderers
  if 'map_renderer' not in st.session_state:
    st.session_state.map_renderer = MapRenderer()
  
  if 'chart_generator' not in st.session_state:
    st.session_state.chart_generator = ChartGenerator()
  
  # UI state
  if 'current_strategy' not in st.session_state:
    st.session_state.current_strategy = 'quality_of_life'
    st.session_state.system.set_strategy(st.session_state.current_strategy)
  
  if 'selected_district' not in st.session_state:
    st.session_state.selected_district = None
  
  if 'selected_districts_comparison' not in st.session_state:
    st.session_state.selected_districts_comparison = None
  
  if 'show_labels' not in st.session_state:
    st.session_state.show_labels = True
  
  if 'top_n' not in st.session_state:
    st.session_state.top_n = 10
  
  # Capas activas del mapa
  if 'active_layers' not in st.session_state:
    st.session_state.active_layers = {
      'districts': True,
      'labels': True
    }
  
  # Modo de comparación
  if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = 'individual'
  
  # Configuración de capas del mapa
  if 'map_layers_config' not in st.session_state:
    st.session_state.map_layers_config = {
      'parks': False,
      'tourist_places': False,
      'crimes': False,
      'metro': False,
      'bus_routes': False,
      'bus_stops': False
    }


def sync_district_selection(selected_from: str, district_name: str):
    """
    Sincroniza selección de distrito entre componentes.
    
    Args:
        selected_from: Fuente de selección
        district_name: Nombre del distrito
    """
    # ... (código existente)
    pass