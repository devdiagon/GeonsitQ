import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.session_state import init_session_state
from visualization.components.header import render_header
from visualization.components.sidebar import render_sidebar
from visualization.pages.map_page import render_map_page
from visualization.pages.rankings_page import render_rankings_page
from visualization.pages.comparison_page import render_comparison_page
from visualization.styles.styles import load_custom_css

st.set_page_config(
    page_title="Sistema de Recomendaciones Urbanas",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========== MAIN APP ==========

def main():
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
        render_map_page()
    
    with tab2:
        render_rankings_page()
    
    with tab3:
        render_comparison_page()
    
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