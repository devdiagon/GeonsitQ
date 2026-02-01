import streamlit as st
import sys
from pathlib import Path

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
    """Inicializa variables de session state."""
    
    # Sistema backend
    if 'system' not in st.session_state:
        with st.spinner('Inicializando sistema...'):
            st.session_state.system = RecommendationSystem(config_path='config.yaml')
        st.success('Sistema inicializado correctamente')
    
    # Renderizadores
    if 'map_renderer' not in st.session_state:
        st.session_state.map_renderer = MapRenderer()
    
    if 'chart_generator' not in st.session_state:
        st.session_state.chart_generator = ChartGenerator()
    
    # Estado de la UI
    if 'current_strategy' not in st.session_state:
        st.session_state.current_strategy = None
    
    if 'selected_district' not in st.session_state:
        st.session_state.selected_district = None
    
    if 'show_labels' not in st.session_state:
        st.session_state.show_labels = True
    
    if 'top_n' not in st.session_state:
        st.session_state.top_n = 10


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
    
    # Radio button para seleccionar estrategia
    selected_display = st.sidebar.radio(
        "Selecciona tu perfil:",
        options,
        index=0 if st.session_state.current_strategy is None else strategy_names.index(st.session_state.current_strategy),
        help="Cada estrategia prioriza diferentes aspectos de los distritos"
    )
    
    # Obtener nombre técnico de la estrategia seleccionada
    selected_strategy = strategy_names[options.index(selected_display)]
    
    # Actualizar estrategia si cambió
    if selected_strategy != st.session_state.current_strategy:
        with st.spinner('Cambiando estrategia...'):
            st.session_state.system.set_strategy(selected_strategy)
            st.session_state.current_strategy = selected_strategy
        st.rerun()
    
    # Mostrar descripción de la estrategia
    if st.session_state.current_strategy:
        strategy_obj = st.session_state.system.get_current_strategy()
        st.sidebar.info(f"**{strategy_obj.get_description()}**")
        
        # Mostrar pesos
        with st.sidebar.expander("Ver pesos de métricas"):
            weights = strategy_obj.get_weights()
            for metric, weight in weights.items():
                if weight > 0:
                    st.write(f"• **{metric.capitalize()}**: {weight*100:.0f}%")
    
    st.sidebar.markdown("---")
    
    # Opciones de visualización
    st.sidebar.markdown("### Opciones de Visualización")
    
    st.session_state.show_labels = st.sidebar.checkbox(
        "Mostrar nombres en mapa",
        value=st.session_state.show_labels,
        help="Muestra etiquetas con nombres de distritos en el mapa"
    )
    
    st.session_state.top_n = st.sidebar.slider(
        "Top N distritos a mostrar",
        min_value=5,
        max_value=20,
        value=st.session_state.top_n,
        step=1,
        help="Número de distritos en rankings y gráficos"
    )
    
    st.sidebar.markdown("---")
    
    # Información del sistema
    st.sidebar.markdown("### Estado del Sistema")
    
    status = st.session_state.system.get_system_status()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Distritos", status['num_districts'])
    with col2:
        st.metric("Estrategias", len(status['available_strategies']))
    
    # Caché
    cache_status = "Activo" if status['cache_valid'] else "⚠️ Inactivo"
    st.sidebar.text(f"Caché: {cache_status}")
    
    st.sidebar.markdown("---")
    
    # Botón de refresh
    if st.sidebar.button("Recalcular Métricas", help="Fuerza recálculo de todas las métricas (ignora caché)"):
        with st.spinner('Recalculando...'):
            st.session_state.system.refresh_analysis()
        st.success("Métricas recalculadas")
        st.rerun()


# ========== HEADER ==========

def render_header():
    """Renderiza el header principal."""
    
    st.markdown('<div class="main-header">Sistema de Recomendaciones Urbanas</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Análisis de Distritos</div>', unsafe_allow_html=True)
    
    # Mostrar estrategia actual
    if st.session_state.current_strategy:
        strategy = st.session_state.system.get_current_strategy()
        st.info(f"**Estrategia Activa**: {strategy.get_name()} - {strategy.get_description()}")


# ========== TAB 1: MAPA INTERACTIVO ==========

def render_map_tab():
    """Renderiza el tab del mapa interactivo."""
    
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
        
        # Agregar controles
        m = st.session_state.map_renderer.add_fullscreen_control(m)
        m = st.session_state.map_renderer.add_minimap(m)
        
        # Agregar LayerControl
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
    
    st.plotly_chart(fig_ranking, use_container_width=True)
    
    # Dos columnas para gráficos adicionales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Distribución de Scores")
        fig_dist = st.session_state.chart_generator.create_score_distribution(
            scores_df=scores_df,
            strategy=strategy
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        st.markdown("#### Correlación entre Métricas")
        fig_corr = st.session_state.chart_generator.create_correlation_heatmap(
            scores_df=scores_df
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    
    # Tabla comparativa
    st.markdown("---")
    st.markdown("#### Tabla Comparativa Detallada")
    
    top_districts = st.session_state.system.get_top_districts(st.session_state.top_n)
    
    fig_table = st.session_state.chart_generator.create_comparison_table(
        top_districts=top_districts
    )
    
    st.plotly_chart(fig_table, use_container_width=True)


# ========== TAB 3: COMPARACIÓN DETALLADA ==========

def render_comparison_tab():
    """Renderiza el tab de comparación detallada."""
    
    st.markdown("### Comparación Detallada")
    
    if st.session_state.current_strategy is None:
        st.warning("Por favor, selecciona una estrategia en el sidebar")
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
    default_selection = all_districts[:3]
    
    selected_districts = st.multiselect(
        "Distritos:",
        options=all_districts,
        default=default_selection,
        max_selections=5,
        help="Selecciona hasta 5 distritos para comparar"
    )
    
    if len(selected_districts) == 0:
        st.info("Selecciona al menos un distrito para ver la comparación")
        return
    
    # Gráfico de comparación de métricas
    st.markdown("#### Comparación de Métricas")
    
    fig_comparison = st.session_state.chart_generator.create_metrics_comparison_chart(
        scores_df=scores_df,
        district_names=selected_districts,
        strategy=strategy
    )
    
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Radar charts individuales
    st.markdown("---")
    st.markdown("#### Análisis Individual")
    
    # Crear columnas según número de distritos seleccionados
    num_cols = min(len(selected_districts), 3)
    cols = st.columns(num_cols)
    
    for i, district_name in enumerate(selected_districts[:3]):
        with cols[i % num_cols]:
            district_data = scores_df[scores_df['district_name'] == district_name].iloc[0]
            
            fig_radar = st.session_state.chart_generator.create_metrics_radar_chart(
                district_data=district_data,
                strategy=strategy
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
    
    # Mostrar más si hay más de 3
    if len(selected_districts) > 3:
        with st.expander(f"Ver {len(selected_districts) - 3} distritos adicionales"):
            cols2 = st.columns(min(len(selected_districts) - 3, 3))
            
            for i, district_name in enumerate(selected_districts[3:]):
                with cols2[i % 3]:
                    district_data = scores_df[scores_df['district_name'] == district_name].iloc[0]
                    
                    fig_radar = st.session_state.chart_generator.create_metrics_radar_chart(
                        district_data=district_data,
                        strategy=strategy
                    )
                    
                    st.plotly_chart(fig_radar, use_container_width=True)


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