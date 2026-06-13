import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from database import get_companies_with_sector, get_indicadores_data
from chart_theme import (
    apply_theme, apply_polar_theme,
    bar_trace, line_trace,
    PALETA, CORES, FONT_COLOR, FONT_COLOR_TITLE, BG_TRANSPARENT,
    GRID_COLOR, ZERO_LINE_COLOR, FONT_FAMILY, LEGEND_BG,
    plot_chart,
)
from ai_analyst import (
    render_ai_panel,
    build_context_indicadores,
    _prompt_indicadores,
)
from glossary import tooltip, chart_tooltip


MAPA_VARIAVEIS = {
    "V00": "Ativo Total",
    "V01": "Ativo Circulante",
    "V02": "Caixa e Equivalentes",
    "V03": "Aplicações Financeiras",
    "V04": "Contas a Receber",
    "V05": "Estoques",
    "V06": "Outros Ativos Circulantes",
    "V07": "Imobilizado",
    "V08": "Ativo Intangível",
    "V09": "Outros Ativos Não Circulantes",
    "V10": "Passivo Circulante",
    "V11": "Fornecedores",
    "V12": "Empréstimos CP",
    "V13": "Outros Passivos Circulantes",
    "V14": "Passivo Não Circulante",
    "V15": "Patrimônio Líquido",
    "V16": "Receita Líquida",
    "V17": "Custo dos Produtos Vendidos",
    "V18": "Lucro Bruto",
    "V19": "Despesas Operacionais",
    "V20": "EBIT",
    "V21": "Resultado Financeiro",
    "V22": "LAIR",
    "V23": "Lucro Líquido",
}

# Cores para composição do ativo
CORES_ATIVO = {
    "V02": CORES["azul"],
    "V04": CORES["verde"],
    "V05": CORES["dourado"],
    "V06": CORES["cinza"],
    "V08": CORES["roxo"],
    "V07": CORES["laranja"],
    "V09": CORES["vermelho"],
}
NOMES_ATIVO = {
    "V02": "Caixa/Equiv.",
    "V04": "Contas a Receber",
    "V05": "Estoques",
    "V06": "Outros Circ.",
    "V08": "Intangível",
    "V07": "Imobilizado",
    "V09": "Outros N.Circ.",
}

def fmt_pct(val, decimais=1):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "—"
    return f"{val * 100:.{decimais}f}%".replace(".", ",")

def fmt_num(val, decimais=2):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "—"
    return f"{val:,.{decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def delta_pct(atual, anterior):
    if anterior is None or (isinstance(anterior, float) and np.isnan(anterior)) or anterior == 0:
        return None
    return (atual - anterior) / abs(anterior)

def safe_get(df, col):
    if col not in df.columns or df[col].dropna().empty:
        return None
    return float(df[col].dropna().iloc[-1])

def safe_get_prev(df, col):
    s = df[col].dropna() if col in df.columns else pd.Series(dtype=float)
    if len(s) < 2:
        return None
    return float(s.iloc[-2])

def card_metric(label, value_str, delta_str=None, delta_color="normal", help_text=None):
    st.metric(label=label, value=value_str, delta=delta_str,
              delta_color=delta_color, help=help_text)

def render_cards_rentabilidade(df):
    st.subheader("Rentabilidade")
    ml_atual  = safe_get(df, "MARGEM_LIQUIDA");  ml_prev  = safe_get_prev(df, "MARGEM_LIQUIDA")
    roe_atual = safe_get(df, "ROE");              roe_prev = safe_get_prev(df, "ROE")
    mb_atual  = safe_get(df, "MARGEM_BRUTA");     mb_prev  = safe_get_prev(df, "MARGEM_BRUTA")
    me_atual  = safe_get(df, "MARGEM_EBIT");      me_prev  = safe_get_prev(df, "MARGEM_EBIT")

    c1, c2, c3, c4 = st.columns(4)
    with c1: card_metric("Margem Líquida",  fmt_pct(ml_atual),
                         fmt_pct(delta_pct(ml_atual, ml_prev)) if ml_prev else None,
                         help_text=tooltip("MARGEM_LIQUIDA"))
    with c2: card_metric("ROE",             fmt_pct(roe_atual),
                         fmt_pct(delta_pct(roe_atual, roe_prev)) if roe_prev else None,
                         help_text=tooltip("ROE"))
    with c3: card_metric("Margem Bruta",    fmt_pct(mb_atual),
                         fmt_pct(delta_pct(mb_atual, mb_prev)) if mb_prev else None,
                         help_text=tooltip("MARGEM_BRUTA"))
    with c4: card_metric("Margem EBIT",     fmt_pct(me_atual),
                         fmt_pct(delta_pct(me_atual, me_prev)) if me_prev else None,
                         help_text=tooltip("MARGEM_EBIT"))

def render_cards_liquidez(df):
    st.subheader("Liquidez & Solvência")
    lc = safe_get(df, "LIQUIDEZ_CORRENTE"); lc_p = safe_get_prev(df, "LIQUIDEZ_CORRENTE")
    ls = safe_get(df, "LIQUIDEZ_SECA");     ls_p = safe_get_prev(df, "LIQUIDEZ_SECA")
    li = safe_get(df, "LIQUIDEZ_IMEDIATA"); li_p = safe_get_prev(df, "LIQUIDEZ_IMEDIATA")
    eg = safe_get(df, "ENDIVIDAMENTO_GERAL"); eg_p = safe_get_prev(df, "ENDIVIDAMENTO_GERAL")

    c1, c2, c3, c4 = st.columns(4)
    with c1: card_metric("Liquidez Corrente", fmt_num(lc),
                         fmt_pct(delta_pct(lc, lc_p)) if lc_p else None,
                         help_text=tooltip("LIQUIDEZ_CORRENTE"))
    with c2: card_metric("Liquidez Seca",     fmt_num(ls),
                         fmt_pct(delta_pct(ls, ls_p)) if ls_p else None,
                         help_text=tooltip("LIQUIDEZ_SECA"))
    with c3: card_metric("Liquidez Imediata", fmt_num(li),
                         fmt_pct(delta_pct(li, li_p)) if li_p else None,
                         help_text=tooltip("LIQUIDEZ_IMEDIATA"))
    with c4:
        dlt = delta_pct(eg, eg_p)
        card_metric("Endividamento Geral", fmt_pct(eg),
                    fmt_pct(dlt) if dlt else None, delta_color="inverse",
                    help_text=tooltip("ENDIVIDAMENTO_GERAL"))

def render_cards_ciclos(df):
    st.subheader("Ciclos Operacionais")
    pmrv = safe_get(df, "PMRV"); pmrv_p = safe_get_prev(df, "PMRV")
    pme  = safe_get(df, "PME")
    co   = safe_get(df, "CICLO_OPERACIONAL")
    cf   = safe_get(df, "CICLO_FINANCEIRO")

    def fmt_dias(v): return f"{v:.0f} d" if v is not None and not np.isnan(v) else "—"

    pmpf = safe_get(df, "PMPF")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        dlt = delta_pct(pmrv, pmrv_p)
        card_metric("PMRV", fmt_dias(pmrv),
                    f"{dlt*100:.1f}%" if dlt else None, delta_color="inverse",
                    help_text=tooltip("PMRV"))
    with c2: card_metric("PME",              fmt_dias(pme),  help_text=tooltip("PME"))
    with c3: card_metric("PMPF",             fmt_dias(pmpf), help_text=tooltip("PMPF"))
    with c4: card_metric("Ciclo Operacional",fmt_dias(co),   help_text=tooltip("CICLO_OPERACIONAL"))
    with c5: card_metric("Ciclo Financeiro", fmt_dias(cf),   help_text=tooltip("CICLO_FINANCEIRO"))

def render_grafico_resultado(df):
    st.subheader("Receita Líquida vs Lucro Líquido", help=chart_tooltip("grafico_resultado"))

    df_p = df[["DT_REFER","V16","V23"]].dropna(subset=["V16"]).sort_values("DT_REFER").copy()
    df_p["DT"] = df_p["DT_REFER"].astype(str)
    df_p["REC"] = df_p["V16"] / 1e6
    df_p["LL"]  = df_p["V23"] / 1e6

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras de receita com gradiente via marker.color array
    fig.add_trace(go.Bar(
        x=df_p["DT"], y=df_p["REC"],
        name="Receita Líquida (MM)",
        marker=dict(
            color=df_p["REC"],
            colorscale=[[0, "rgba(56,189,248,0.45)"], [1, "rgba(56,189,248,0.85)"]],
            showscale=False,
            line=dict(width=0),
        ),
        hovertemplate="Receita: R$ %{y:,.1f}M<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df_p["DT"], y=df_p["LL"],
        name="Lucro Líquido (MM)",
        mode="lines+markers+text",
        line=dict(color=CORES["roxo"], width=3),
        marker=dict(size=8, color=CORES["roxo"],
                    line=dict(width=2, color="rgba(255,255,255,0.3)")),
        fill="tozeroy",
        fillcolor="rgba(206,147,216,0.18)",
        text=[f"R${v:,.1f}M" for v in df_p["LL"]],
        textposition="top center",
        textfont=dict(size=10, color=CORES["roxo"]),
        hovertemplate="Lucro: R$ %{y:,.1f}M<extra></extra>",
    ), secondary_y=True)


    apply_theme(fig, height=400,
                y_title="Receita (R$ MM)",
                y2_title="Lucro (R$ MM)",
                x_is_category=True)
    plot_chart(fig)

def render_grafico_margens(df):
    st.subheader("Evolução das Margens", help=chart_tooltip("grafico_margens"))

    config = {
        "MARGEM_BRUTA":   ("Margem Bruta",   CORES["verde"]),
        "MARGEM_EBIT":    ("Margem EBIT",     CORES["azul"]),
        "MARGEM_LIQUIDA": ("Margem Líquida",  CORES["roxo"]),
        "ROA":            ("ROA",             CORES["dourado"]),
        "ROE":            ("ROE",             CORES["laranja"]),
    }

    df_p = df[["DT_REFER"] + list(config)].dropna(subset=["MARGEM_LIQUIDA"]).sort_values("DT_REFER")
    df_p["DT"] = df_p["DT_REFER"].astype(str)

    fig = go.Figure()
    for col, (nome, cor) in config.items():
        if col in df_p.columns:
            fig.add_trace(go.Scatter(
                x=df_p["DT"], y=df_p[col] * 100,
                name=nome,
                mode="lines+markers",
                line=dict(color=cor, width=2.5),
                marker=dict(size=7, color=cor,
                            line=dict(width=1.5, color="rgba(255,255,255,0.25)")),
                hovertemplate=f"{nome}: %{{y:.1f}}%<extra></extra>",
            ))

    fig.add_hline(y=0, line_dash="dot",
                  line_color="rgba(255,255,255,0.25)", line_width=1)
    apply_theme(fig, height=380, y_title="(%)", y_suffix="%", x_is_category=True)
    plot_chart(fig)

def render_grafico_composicao_ativo(df):
    st.subheader("Composição do Ativo Total", help=chart_tooltip("grafico_composicao_ativo"))

    cols = list(CORES_ATIVO.keys())
    df_p = df[["DT_REFER"] + cols].sort_values("DT_REFER").copy()
    df_p["DT"] = df_p["DT_REFER"].astype(str)

    fig = go.Figure()
    for col in cols:
        if col in df_p.columns:
            cor = CORES_ATIVO[col]
            nome = NOMES_ATIVO[col]
            vals = df_p[col].fillna(0) / 1e6
            fig.add_trace(go.Bar(
                x=df_p["DT"], y=vals, name=nome,
                marker=dict(color=cor, opacity=0.85, line=dict(width=0)),
                hovertemplate=f"{nome}: R$ %{{y:,.1f}}M<extra></extra>",
            ))

    fig.update_layout(barmode="stack")
    apply_theme(fig, height=420, y_title="R$ Milhões", x_is_category=True)
    plot_chart(fig)

def render_grafico_intangivel(df):
    st.subheader("Intangível sobre Ativo Total", help=chart_tooltip("grafico_intangivel"))

    df_p = df[["DT_REFER","V00","V08"]].dropna(subset=["V00","V08"]).sort_values("DT_REFER").copy()
    df_p["DT"]         = df_p["DT_REFER"].astype(str)
    df_p["PART"]       = df_p["V08"] / df_p["V00"] * 100
    df_p["INTANG_MM"]  = df_p["V08"] / 1e6

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=df_p["DT"], y=df_p["INTANG_MM"],
        name="Intangível (MM)",
        marker=dict(
            color=df_p["INTANG_MM"],
            colorscale=[[0, "rgba(159,168,218,0.4)"], [1, "rgba(159,168,218,0.9)"]],

            showscale=False,
            line=dict(width=0),
        ),
        hovertemplate="Intangível: R$ %{y:,.1f}M<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df_p["DT"], y=df_p["PART"],
        name="% Ativo Total",
        mode="lines+markers+text",
        line=dict(color=CORES["dourado"], width=3, dash="dash"),
        marker=dict(size=8, color=CORES["dourado"],
                    line=dict(width=1.5, color="rgba(255,255,255,0.3)")),
        text=[f"{v:.1f}%" for v in df_p["PART"]],
        textposition="top center",
        textfont=dict(size=10, color=CORES["dourado"]),
        hovertemplate="Participação: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)

    apply_theme(fig, height=380,
                y_title="Intangível (R$ MM)",
                y2_title="% sobre Ativo Total",
                x_is_category=True)
    plot_chart(fig)

def render_grafico_ncg(df):
    st.subheader("Necessidade de Capital de Giro (NCG)", help=chart_tooltip("grafico_ncg"))

    config_ncg = {
        "NCG": ("NCG",               CORES["roxo"],   "bar"),
        "ST":  ("Saldo Tesouraria",   CORES["laranja"],"bar"),
        "CGL": ("CGL",               CORES["azul"],   "line"),
        "CGP": ("CGP",               CORES["verde"],  "line"),
    }

    df_p = df[["DT_REFER"] + [c for c in config_ncg if c in df.columns]].sort_values("DT_REFER").copy()
    df_p["DT"] = df_p["DT_REFER"].astype(str)

    fig = go.Figure()
    for col, (nome, cor, tipo) in config_ncg.items():
        if col not in df_p.columns:
            continue
        vals = df_p[col].fillna(0) / 1e6
        if tipo == "bar":
            fig.add_trace(go.Bar(
                x=df_p["DT"], y=vals, name=nome,
                marker=dict(color=cor, opacity=0.80, line=dict(width=0)),
                hovertemplate=f"{nome}: R$ %{{y:,.1f}}M<extra></extra>",
            ))
        else:
            fig.add_trace(go.Scatter(
                x=df_p["DT"], y=vals, name=nome,
                mode="lines+markers",
                line=dict(color=cor, width=2.5, dash="dot"),
                marker=dict(size=7, color=cor,
                            line=dict(width=1.5, color="rgba(255,255,255,0.25)")),
                hovertemplate=f"{nome}: R$ %{{y:,.1f}}M<extra></extra>",
            ))

    fig.add_hline(y=0, line_dash="dot",
                  line_color="rgba(255,255,255,0.25)", line_width=1)
    fig.update_layout(barmode="group")
    apply_theme(fig, height=380, y_title="R$ Milhões", x_is_category=True)
    plot_chart(fig)

def render_tabela_indicadores(df):
    with st.expander("📋 Tabela Completa de Indicadores", expanded=False):
        df_tab = df.copy()
        df_tab["DT_REFER"] = df_tab["DT_REFER"].astype(str)

        indicadores = {
            "DT_REFER":                  "Data",
            "MARGEM_BRUTA":              "Margem Bruta",
            "MARGEM_EBIT":               "Margem EBIT",
            "MARGEM_LIQUIDA":            "Margem Líquida",
            "ROA":                       "ROA",
            "ROE":                       "ROE",
            "LIQUIDEZ_CORRENTE":         "Liq. Corrente",
            "LIQUIDEZ_SECA":             "Liq. Seca",
            "LIQUIDEZ_IMEDIATA":         "Liq. Imediata",
            "LIQUIDEZ_GERAL":            "Liq. Geral",
            "ENDIVIDAMENTO_GERAL":       "Endividamento",
            "GRAU_ENDIVIDAMENTO":        "Grau Endivid.",
            "COMPOSICAO_ENDIVIDAMENTO":  "Comp. Endivid.",
            "DIVIDA_LIQUIDA":            "Dívida Líquida",
            "PMRV":                      "PMRV (dias)",
            "PME":                       "PME (dias)",
            "PMPF":                      "PMPF (dias)",
            "CICLO_OPERACIONAL":         "Ciclo Oper.",
            "CICLO_FINANCEIRO":          "Ciclo Fin.",
            "NCG":                       "NCG",
            "CGL":                       "CGL",
            "CGP":                       "CGP",
            "ST":                        "Saldo Tesour.",
        }
        pct_cols_orig = ["MARGEM_BRUTA","MARGEM_EBIT","MARGEM_LIQUIDA",
                         "ROA","ROE","ENDIVIDAMENTO_GERAL","COMPOSICAO_ENDIVIDAMENTO"]

        cols_ok = [c for c in indicadores if c in df_tab.columns]
        df_v = df_tab[cols_ok].rename(columns=indicadores).sort_values("Data", ascending=False)
        for col_orig, col_label in {indicadores[c]: c for c in pct_cols_orig
                                     if c in df_tab.columns}.items():
            if col_orig in df_v.columns:
                df_v[col_orig] = df_v[col_orig].apply(
                    lambda x: fmt_pct(x) if x is not None and not (isinstance(x, float) and np.isnan(x)) else "—"
                )
        st.dataframe(df_v, hide_index=True, use_container_width=True)

def render_gauges_rentabilidade(df):
    """Velocímetros para os principais indicadores do último período."""
    st.subheader("Painel de Indicadores — Último Período")

    def gauge(titulo, valor, fmt, min_v, max_v, zonas, ajuda=None):
        if valor is None or (isinstance(valor, float) and np.isnan(valor)):
            return go.Figure()
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=valor * 100 if fmt == "pct" else valor,
            number=dict(
                suffix="%" if fmt == "pct" else "x",
                font=dict(color=FONT_COLOR_TITLE, size=26, family=FONT_FAMILY),
            ),
            title=dict(text=titulo, font=dict(color=FONT_COLOR, size=13, family=FONT_FAMILY)),
            gauge=dict(
                axis=dict(range=[min_v, max_v], tickfont=dict(color=FONT_COLOR, size=9)),
                bar=dict(color=PALETA[0], thickness=0.3),
                bgcolor="rgba(232,241,242,0.5)",
                borderwidth=1, bordercolor="rgba(19,41,61,0.10)",
                steps=[dict(range=[r[0], r[1]], color=r[2]) for r in zonas],
                threshold=dict(line=dict(color=PALETA[3], width=2),
                               thickness=0.75, value=valor * 100 if fmt == "pct" else valor),
            ),
        ))
        fig.update_layout(
            paper_bgcolor=BG_TRANSPARENT,
            font=dict(family=FONT_FAMILY, color=FONT_COLOR),
            height=220, margin=dict(t=40, b=10, l=20, r=20),
        )
        return fig

    zonas_ml  = [(-50, 0, "#F4A8A8"), (0, 10, "#FEFCC8"), (10, 100, "#B8DFB3")]
    zonas_roe = [(-50, 0, "#F4A8A8"), (0, 10, "#FEFCC8"), (10, 100, "#B8DFB3")]
    zonas_lc  = [(0, 1, "#F4A8A8"), (1, 1.5, "#FEFCC8"), (1.5, 5, "#B8DFB3")]
    zonas_eg  = [(0, 40, "#B8DFB3"), (40, 70, "#FEFCC8"), (70, 100, "#F4A8A8")]

    ml  = safe_get(df, "MARGEM_LIQUIDA")
    roe = safe_get(df, "ROE")
    lc  = safe_get(df, "LIQUIDEZ_CORRENTE")
    eg  = safe_get(df, "ENDIVIDAMENTO_GERAL")

    c1, c2, c3, c4 = st.columns(4)
    with c1: plot_chart(gauge("Margem Líquida", ml, "pct", -50, 100, zonas_ml,
                              tooltip("MARGEM_LIQUIDA")))
    with c2: plot_chart(gauge("ROE", roe, "pct", -50, 100, zonas_roe,
                              tooltip("ROE")))
    with c3: plot_chart(gauge("Liquidez Corrente", lc, "num", 0, 5, zonas_lc,
                              tooltip("LIQUIDEZ_CORRENTE")))
    with c4: plot_chart(gauge("Endividamento Geral", eg, "pct", 0, 100, zonas_eg,
                              tooltip("ENDIVIDAMENTO_GERAL")))


def render_indicadores_page():

    selected_cnpj = st.session_state.get("global_cnpj")
    selected_label = st.session_state.get("global_label", "")
    if not selected_cnpj:
        st.warning("Selecione uma empresa na barra lateral.")
        return

    with st.sidebar:
        df_all = get_indicadores_data(selected_cnpj)
        if df_all.empty:
            st.error("Sem dados para esta empresa.")
            return

        datas_disp = sorted(df_all["DT_REFER"].astype(str).unique(), reverse=True)
        selected_dates = st.multiselect(
            "Períodos:",
            options=datas_disp,
            default=datas_disp[:8] if len(datas_disp) >= 8 else datas_disp,
            key="sel_datas_indicadores",
        )
        if not selected_dates:
            st.warning("Selecione ao menos uma data.")
            return

        st.markdown("---")
        for campo, emoji in [("SETOR", "🏢"), ("TP_MERC", "📋")]:
            vals = df_all[campo].dropna().unique() if campo in df_all.columns else []
            if len(vals):
                st.info(f"{emoji} **{campo.replace('_',' ').title()}:** {vals[0]}")

    df = df_all[df_all["DT_REFER"].astype(str).isin(selected_dates)].sort_values("DT_REFER")

    nome_empresa = selected_label.split(" (")[0]
    razao = (df["RAZAO_SOCIAL"].dropna().iloc[-1]
             if "RAZAO_SOCIAL" in df.columns and not df["RAZAO_SOCIAL"].dropna().empty
             else nome_empresa)

    st.title(f"{razao}")
    st.caption(
        f"**CNPJ:** {selected_cnpj} | **Indicadores Financeiros** | "
        f"Períodos: {', '.join(sorted(selected_dates))}"
    )
    st.markdown("---")

    render_gauges_rentabilidade(df)
    st.markdown("---")

    render_cards_rentabilidade(df)
    st.markdown("###")
    render_cards_liquidez(df)
    st.markdown("###")
    render_cards_ciclos(df)
    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a: render_grafico_resultado(df)
    with col_b: render_grafico_margens(df)

    st.markdown("###")

    col_c, col_d = st.columns(2)
    with col_c: render_grafico_composicao_ativo(df)
    with col_d: render_grafico_intangivel(df)

    st.markdown("###")
    render_grafico_ncg(df)

    st.markdown("---")
    contexto_ia = build_context_indicadores(df, razao)
    render_ai_panel(
        contexto=contexto_ia,
        prompt_fn=lambda ctx: _prompt_indicadores(ctx, razao),
        titulo="Análise da IA — Indicadores Financeiros",
        panel_key=f"ind_{selected_cnpj}",
    )

    st.markdown("---")
    render_tabela_indicadores(df)

    with st.expander("📖 Glossário de Variáveis (V00 – V23)"):
        cols = st.columns(3)
        items = list(MAPA_VARIAVEIS.items())
        chunk = len(items) // 3 + 1
        for i, col in enumerate(cols):
            with col:
                for k, v in items[i * chunk:(i + 1) * chunk]:
                    st.markdown(f"**{k}** — {v}")
