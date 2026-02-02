import streamlit as st


def render_header():
  st.markdown('<div class="main-header">Sistema de Recomendaciones Urbanas</div>', unsafe_allow_html=True)
  st.markdown('<div class="sub-header">Análisis de Distritos</div>', unsafe_allow_html=True)