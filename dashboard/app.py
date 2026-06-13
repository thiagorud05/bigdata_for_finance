import streamlit as st
import os
from dotenv import load_dotenv

from config import PAGE_CONFIG
from database import get_companies_bp
from views.balanco_patrimonial import render_bp_page
from views.indicadores_financeiros import render_indicadores_page
from views.comparativo import render_comparativo_page
from views.dre import render_dre_page
from views.dfc import render_dfc_page
from views.sobre import render_sobre_page

st.set_page_config(**PAGE_CONFIG)

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

#  Brand CSS 
st.markdown(""" <style>
/*  Variáveis de marca  */
:root {
    --prussian:  #13293D;
    --sapphire:  #006494;
    --celadon:   #247BA0;
    --carolina:  #1B98E0;
    --azure:     #E8F1F2;
    --azure-mid: #D0E8EE;
}

/*  Sidebar  */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--prussian) 0%, var(--sapphire) 100%) !important;
}
/* Texto geral do sidebar */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stRadio label {
    color: var(--azure) !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(232,241,242,0.20) !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdown"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: rgba(232,241,242,0.70) !important;
}
/* Selecionado no radio sidebar */
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + label {
    color: #1B98E0 !important;
    font-weight: 600;
}

/* Sidebar: selectbox e multiselect — fundo escuro + texto claro */
[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
    background-color: rgba(19, 41, 61, 0.50) !important;
    border-color: rgba(232, 241, 242, 0.28) !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child * {
    color: var(--azure) !important;
    background-color: transparent !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child:focus-within {
    border-color: var(--carolina) !important;
    box-shadow: 0 0 0 2px rgba(27,152,224,0.25) !important;
}
/* Tags multiselect no sidebar */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: rgba(27, 152, 224, 0.35) !important;
    border: 1px solid rgba(232, 241, 242, 0.20) !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span {
    color: var(--azure) !important;
}

/*  Títulos principais  */
h1 { color: var(--prussian) !important; }
h2 { color: var(--sapphire) !important; }
h3 { color: var(--celadon)  !important; }

/*  Métricas (st.metric)  */
[data-testid="stMetricLabel"] {
    color: var(--sapphire) !important;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    color: var(--prussian) !important;
}
[data-testid="stMetricDelta"] svg { display: none; }

/*  Botões  */
.stButton > button {
    background: var(--carolina) !important;
    color: var(--azure) !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: background 0.2s ease;
}
.stButton > button:hover {
    background: var(--sapphire) !important;
}

/*  Tabelas / DataFrames  */
[data-testid="stDataFrame"] thead th {
    background: var(--prussian) !important;
    color: var(--azure) !important;
}

/*  Expander  */
[data-testid="stExpander"] summary {
    background: var(--azure-mid) !important;
    color: var(--prussian) !important;
    border-radius: 6px;
    font-weight: 600;
}

/*  Info / Warning / Success / Error  */
[data-testid="stAlert"][data-baseweb="notification"] {
    border-left: 4px solid var(--carolina) !important;
    background: var(--azure-mid) !important;
}

/*  Slider  */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: var(--carolina) !important;
}

/*  Selectbox / Multiselect / Input text  */
/* Texto digitado e valor selecionado — força cor escura */
[data-baseweb="select"] input,
[data-baseweb="select"] [data-testid="stSelectboxVirtualDropdown"],
[data-baseweb="select"] div[class*="ValueContainer"] span,
[data-baseweb="select"] div[class*="singleValue"],
[data-baseweb="select"] div[class*="placeholder"] {
    color: var(--prussian) !important;
}

/* Opções da lista suspensa (popup fora do sidebar) */
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"] [role="option"] {
    color: var(--prussian) !important;
    background: var(--azure) !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu"] [role="option"]:hover,
[data-baseweb="popover"] [aria-selected="true"][role="option"],
[data-baseweb="menu"] [aria-selected="true"][role="option"] {
    background: var(--azure-mid) !important;
    color: var(--sapphire) !important;
}

/* Tags do multiselect */
[data-baseweb="tag"] {
    background: var(--carolina) !important;
    color: var(--azure) !important;
}
[data-baseweb="tag"] span { color: var(--azure) !important; }

/* Borda do select */
[data-baseweb="select"] > div:first-child {
    border-color: var(--celadon) !important;
}
[data-baseweb="select"] > div:first-child:focus-within {
    border-color: var(--carolina) !important;
    box-shadow: 0 0 0 2px rgba(27,152,224,0.22) !important;
}


/*  Caption e pequenos textos  */
[data-testid="stCaptionContainer"] {
    color: var(--celadon) !important;
}

/*  Linha horizontal (---)  */
hr {
    border-color: var(--azure-mid) !important;
}

/*  Scrollbar  */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--azure); }
::-webkit-scrollbar-thumb { background: var(--celadon); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--sapphire); }

/* ═══════════════════════════════════════════════════════════
   RESPONSIVO — MOBILE  (≤ 768 px)
   Não altera nada no desktop; só entra em telas pequenas.
   ═══════════════════════════════════════════════════════════ */
@media (max-width: 768px) {

    /* ── Área principal — menos padding lateral ── */
    .block-container {
        padding-left: 0.75rem  !important;
        padding-right: 0.75rem !important;
        padding-top: 1rem      !important;
    }

    /* ── Títulos menores ── */
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.15rem !important; }
    h3 { font-size: 1rem   !important; }

    /* ── Colunas: wrap + 2 por linha (grade 2×2 para métricas) ──
       O Streamlit seta width inline nos st.Column → precisamos
       de !important em width também para sobrescrever.           */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        min-width: calc(50% - 0.4rem) !important;
        max-width: calc(50% - 0.4rem) !important;
        width:     calc(50% - 0.4rem) !important;
        flex: 1 1  calc(50% - 0.4rem) !important;
    }

    /* ── Métricas: fontes ajustadas para caber em 50% da tela ── */
    [data-testid="stMetricValue"] {
        font-size: 1.05rem !important;
        line-height: 1.2   !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.70rem !important;
    }

    /* ── Heatmap: scroll horizontal + aviso mobile ── */
    .mobile-heatmap-hint {
        display: block !important;
        background: #D0E8EE;
        border-left: 4px solid #1B98E0;
        padding: 0.6rem 1rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #13293D;
        margin-bottom: 0.75rem;
    }
    /* Gráficos: scroll lateral caso o conteúdo extravase */
    [data-testid="stPlotlyChart"] {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }

    /* ── DataFrames: scroll horizontal ── */
    [data-testid="stDataFrame"] {
        overflow-x: auto !important;
    }

    /* ── Expanders: margem menor ── */
    [data-testid="stExpander"] {
        margin-bottom: 0.5rem !important;
    }

    /* ── Botões: largura total ── */
    .stButton > button {
        width: 100% !important;
        margin-bottom: 0.4rem !important;
    }

    /* ── Selectbox e multiselect: maior área de toque ── */
    [data-baseweb="select"] > div:first-child {
        min-height: 44px !important;
    }

    /* ── Chat input: não sai da tela ── */
    [data-testid="stChatInput"] {
        max-width: 100% !important;
    }

    /* ── Slider: maior área de toque ── */
    [data-baseweb="slider"] [role="slider"] {
        width: 24px  !important;
        height: 24px !important;
    }
}

/* O aviso de heatmap fica oculto no desktop por padrão */
.mobile-heatmap-hint { display: none; }

</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.title("Data Lake CVM")
    st.caption("Disciplina: Big Data for Finance - FAE")
    st.markdown("---")
    pagina = st.radio( "Navegação",
        options=[ " Balanço Patrimonial", " DRE", " DFC", " Indicadores Financeiros", " Comparativo de Empresas", " Sobre o Projeto",
        ],
        index=0,
    )

    if pagina in [" Balanço Patrimonial", " DRE", " DFC", " Indicadores Financeiros"]:
        st.markdown("---")
        st.header("Filtros de Análise")
        df_empresas = get_companies_bp()
        if not df_empresas.empty:
            mapa_empresas = dict(zip(df_empresas['LABEL_DROPDOWN'], df_empresas['CNPJ_CIA']))
            options_emp = df_empresas['LABEL_DROPDOWN'].tolist()
            
            saved_cnpj = st.session_state.get("global_cnpj", None)
            default_idx = 0
            if saved_cnpj:
                for i, lbl in enumerate(options_emp):
                    if saved_cnpj in lbl:
                        default_idx = i
                        break
            
            selected_label = st.selectbox(
                "Selecione a Empresa:",
                options=options_emp,
                index=default_idx,
                key="global_empresa_select",
            )
            selected_cnpj = mapa_empresas[selected_label]
            st.session_state["global_cnpj"] = selected_cnpj
            st.session_state["global_label"] = selected_label

if pagina == " Balanço Patrimonial":
    render_bp_page()
elif pagina == " DRE":
    render_dre_page()
elif pagina == " DFC":
    render_dfc_page()
elif pagina == " Indicadores Financeiros":
    render_indicadores_page()
elif pagina == " Comparativo de Empresas":
    render_comparativo_page()
elif pagina == " Sobre o Projeto":
    render_sobre_page()

st.markdown("---")
c1, c2 = st.columns([3, 1])
with c1: st.caption("Desenvolvido para fins didáticos de análise de dados CVM.")
with c2: st.caption("© 2025 Alunos do curso de Ciência de Dados para Negócios - FAE Centro Universitário")