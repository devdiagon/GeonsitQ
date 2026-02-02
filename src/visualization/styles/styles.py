import streamlit as st
from pathlib import Path


def load_custom_css():
  css_file = Path(__file__).parent / "styles.css"
  
  if css_file.exists():
    with open(css_file, 'r', encoding='utf-8') as f:
      css_content = f.read()
    
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
  else:
    st.warning("Archivo styles.css no encontrado")