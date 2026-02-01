import streamlit as st
import sys
from pathlib import Path
import time
from datetime import datetime
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from integration.backend_facade import RecommendationSystem
from visualization.map_renderer import MapRenderer
from visualization.chart_generator import ChartGenerator

st.set_page_config(
    page_title="Sistema de Recomendaciones Urbanas",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========== CUSTOM CSS ==========

def load_custom_css():
    st.markdown("""
    <style>
        /* Header principal */
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1976D2;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        /* Subheader */
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* Métricas personalizadas */
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1976D2;
        }
        
        /* Sidebar */
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
            font-size: 1.1rem;
        }
        
        /* Botones */
        .stButton>button {
            width: 100%;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
        }
    </style>
    """, unsafe_allow_html=True)


# ========== INICIALIZACIÓN DE SESSION STATE ==========

def init_session_state():
    
    # Sistema backend
    if 'system' not in st.session_state:
        with st.spinner('Inicializando sistema...'):
            st.session_state.system = RecommendationSystem(config_path='config.yaml')
            st.session_state.init_time = datetime.now()
    
    # Renderizadores
    if 'map_renderer' not in st.session_state:
        st.session_state.map_renderer = MapRenderer()
    
    if 'chart_generator' not in st.session_state:
        st.session_state.chart_generator = ChartGenerator()
    
    # Estado de la UI
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

# ========== CALLBACKS ==========

def on_strategy_change():    
    # Actualizar estrategia
    st.session_state.current_strategy = st.session_state.temp_strategy
    
    # Aplicar cambio en el backend
    with st.spinner('Actualizando análisis...'):
        st.session_state.system.set_strategy(st.session_state.current_strategy)


def on_district_select():
    st.session_state.selected_district = st.session_state.temp_selected_district


def on_visualization_option_change():
    st.session_state.force_map_update = True


# ========== SIDEBAR ==========

def render_sidebar():
    """Renderiza el sidebar con controles."""
    
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
    
    # Opciones de visualización
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
    
    # ========== CAPAS ADICIONALES DEL MAPA ==========
    
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
    
    # Información del sistema
    st.sidebar.markdown("### Estado del Sistema")
    
    status = st.session_state.system.get_system_status()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Distritos", status['num_districts'])
    with col2:
        st.metric("Estrategias", len(status['available_strategies']))
    
    st.sidebar.markdown("---")
    
    # Acciones
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


# ========== HEADER ==========

def render_header():
    st.markdown('<div class="main-header">Sistema de Recomendaciones Urbanas</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Análisis de Distritos</div>', unsafe_allow_html=True)


# ========== TAB 1: MAPA INTERACTIVO ==========

def render_map_tab():    
    st.markdown("### Mapa de Distritos por Score")
    
    if st.session_state.current_strategy is None:
        st.warning("Por favor, selecciona una estrategia en el sidebar")
        return
    
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


# ========== TAB 2: RANKINGS Y ESTADÍSTICAS ==========

def render_rankings_tab():
    """Renderiza el tab de rankings."""
    
    st.markdown("### Rankings y Estadísticas")
    
    if st.session_state.current_strategy is None:
        st.warning("Por favor, selecciona una estrategia en el sidebar")
        return
    
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
    st.markdown("#### Tabla Comparativa Detallada")
    
    top_districts = st.session_state.system.get_top_districts(st.session_state.top_n)
    
    fig_table = st.session_state.chart_generator.create_comparison_table(
        top_districts=top_districts
    )
    
    st.plotly_chart(fig_table, width='stretch')


# ========== TAB 3: COMPARACIÓN DETALLADA ==========

def render_comparison_tab():    
    st.markdown("### Comparación Detallada")
    
    if st.session_state.current_strategy is None:
        st.warning("Por favor, selecciona una estrategia en el sidebar")
        return
    
    # Verificar modo de comparación
    if st.session_state.comparison_mode == 'multi_strategy':
        render_multi_strategy_comparison()
        return

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

    # Gráfico de comparación de métricas
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
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, width='stretch', hide_index=True)

# ========== ANÁLISIS MULTI-ESTRATEGIA ==========

def get_all_strategy_scores():
    """Obtiene scores de todas las estrategias."""
    
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


# ========== MAIN APP ==========

def main():
    """Función principal de la aplicación."""
    
    # Cargar CSS personalizado
    load_custom_css()
    
    # Inicializar session state
    init_session_state()
    
    # Renderizar sidebar
    render_sidebar()
    
    # Renderizar header
    render_header()
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs([
        "Mapa Interactivo",
        "Rankings y Estadísticas",
        "Comparación Detallada"
    ])
    
    with tab1:
        render_map_tab()
    
    with tab2:
        render_rankings_tab()
    
    with tab3:
        render_comparison_tab()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.9rem;'>
            Sistema de Recomendaciones Urbanas 2026
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()