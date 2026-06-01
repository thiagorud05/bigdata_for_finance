import streamlit as st
import os
from dotenv import load_dotenv

from config import PAGE_CONFIG
from views.balanco_patrimonial import render_bp_page
from views.indicadores_financeiros import render_indicadores_page
from views.comparativo import render_comparativo_page
from views.dre import render_dre_page
from views.dfc import render_dfc_page

st.set_page_config(**PAGE_CONFIG)

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

with st.sidebar:
    st.title("Data Lake CVM")
    st.caption("Disciplina: Big Data for Finance - FAE")
    st.markdown("---")
    pagina = st.radio(
        "Navegação",
        options=[
            "📑 Balanço Patrimonial",
            "📋 DRE",
            "💰 DFC",
            "📊 Indicadores Financeiros",
            "🔍 Comparativo de Empresas",
        ],
        index=0,
    )

if pagina == "📑 Balanço Patrimonial":
    render_bp_page()
elif pagina == "📋 DRE":
    render_dre_page()
elif pagina == "💰 DFC":
    render_dfc_page()
elif pagina == "📊 Indicadores Financeiros":
    render_indicadores_page()
elif pagina == "🔍 Comparativo de Empresas":
    render_comparativo_page()

st.markdown("---")
c1, c2 = st.columns([3, 1])
with c1: st.caption("Desenvolvido para fins didáticos de análise de dados CVM.")
with c2: st.caption("© 2025 Alunos do curso de Ciência de Dados para Negócios - FAE Centro Universitário")