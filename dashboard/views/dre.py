"""
Demonstração do Resultado do Exercício (DRE)
Segue o mesmo padrão visual do Balanço Patrimonial, com gráficos
específicos para análise de resultados: cascata (waterfall) e margens.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from database import get_companies_demonstrativo, get_dates_demonstrativo, get_demonstrativo_filtered
from chart_theme import (
    BG_TRANSPARENT, GRID_COLOR, ZERO_LINE_COLOR,
    FONT_COLOR, FONT_COLOR_TITLE, PALETA, FONT_FAMILY, LEGEND_BG,
    apply_theme,
)
from ai_analyst import (
    render_ai_panel,
    build_context_dre,
    _prompt_dre,
)

def formatar_moeda_br(valor):
    if pd.isna(valor):
        return "-"
    texto = f"{valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")

def _pivot_e_datas(df_raw, divisor):
    """Pivota o DataFrame e retorna (df_pivot, cols_dates)."""
    df_raw = df_raw.copy()
    df_raw["VL_CONTA_TRATADO"] = df_raw["VL_CONTA_TRATADO"] / divisor

    df_pivot = df_raw.pivot_table(
        values="VL_CONTA_TRATADO",
        index=["CD_CONTA", "DS_CONTA"],
        columns="DT_REFER",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    df_pivot.columns = [
        c.strftime("%Y-%m-%d") if hasattr(c, "strftime") else c
        for c in df_pivot.columns
    ]
    cols_dates = sorted([c for c in df_pivot.columns if c not in ["CD_CONTA", "DS_CONTA"]])
    df_pivot = df_pivot[["CD_CONTA", "DS_CONTA"] + cols_dates]
    return df_pivot, cols_dates

def _get_serie(df_pivot, prefix, cols_dates):
    """Retorna a série temporal da conta-raiz (ex: '3' ou '3.01')."""
    rows = df_pivot[df_pivot["CD_CONTA"] == prefix]
    if rows.empty:
        return pd.Series(0.0, index=cols_dates)
    return rows[cols_dates].iloc[0]

def _get_conta(df_pivot, code, cols_dates):
    """Valor de uma conta específica como Series."""
    r = df_pivot[df_pivot["CD_CONTA"] == code]
    if r.empty:
        return pd.Series(0.0, index=cols_dates)
    return r[cols_dates].iloc[0]

def _show_table(df_input, titulo, scale_option, cols_dates):
    st.subheader(titulo)
    df_v = df_input.copy()
    for c in cols_dates:
        df_v[c] = df_v[c].apply(formatar_moeda_br)
    altura = min((len(df_v) + 1) * 35 + 3, 800)
    col_cfg = {
        "CD_CONTA": st.column_config.TextColumn("Conta", width="small"),
        "DS_CONTA": st.column_config.TextColumn("Descrição", width="medium"),
        **{c: st.column_config.TextColumn(c, width="small") for c in cols_dates},
    }
    st.dataframe(df_v, hide_index=True, use_container_width=True,
                 column_config=col_cfg, height=altura)

def _render_waterfall(df_pivot, cols_dates, scale_option):
    st.subheader("📊 Cascata do Resultado (último período)")

    dt_ref = cols_dates[-1]

    def val(code):
        r = df_pivot[df_pivot["CD_CONTA"] == code]
        return float(r[dt_ref].iloc[0]) if not r.empty else None

    # Contas-chave da DRE (CVM padrão)
    contas = [
        ("3.01", "Receita Líquida"),
        ("3.02", "(-) CPV / CSP"),
        ("3.03", "Lucro Bruto"),
        ("3.04", "(-) Desp. Operac."),
        ("3.05", "EBIT"),
        ("3.06", "Res. Financeiro"),
        ("3.07", "LAIR"),
        ("3.08", "(-) IR / CSLL"),
        ("3.11", "Lucro Líquido"),
    ]

    labels, vals, medidas, textos, cores = [], [], [], [], []

    ref_val = val("3.01") or val("3")  # Receita como âncora
    if ref_val is None:
        st.info("Não foi possível identificar a conta de Receita (3.01) para o waterfall.")
        return

    for code, label in contas:
        v = val(code)
        if v is None:
            continue

        labels.append(label)
        if label in ("Receita Líquida", "Lucro Bruto", "EBIT", "LAIR", "Lucro Líquido"):
            medidas.append("absolute")
            cores.append(PALETA[2] if v >= 0 else PALETA[7])
        else:
            medidas.append("relative")
            cores.append(PALETA[7] if v < 0 else PALETA[2])
        vals.append(v)
        textos.append(formatar_moeda_br(v))

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=medidas,
        x=labels,
        y=vals,
        text=textos,
        textposition="outside",
        textfont=dict(color=FONT_COLOR, size=10),
        connector=dict(line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot")),
        increasing=dict(marker_color=PALETA[2]),
        decreasing=dict(marker_color=PALETA[7]),
        totals=dict(marker_color=PALETA[0]),
        hovertemplate="%{x}: %{text}<extra></extra>",
    ))

    apply_theme(fig, height=420, y_title=f"Valor ({scale_option})", x_is_category=True)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"📅 Período de referência: **{dt_ref}**")

def _render_evolucao_resultado(df_pivot, cols_dates, scale_option):
    st.subheader("📈 Evolução Temporal — Receita, Resultado Bruto e Lucro Líquido")

    series = {
        "Receita Líquida": ("3.01", PALETA[1]),
        "Lucro Bruto":     ("3.03", PALETA[2]),
        "EBIT":            ("3.05", PALETA[5]),
        "Lucro Líquido":   ("3.11", PALETA[0]),
    }

    fig = go.Figure()
    for nome, (code, cor) in series.items():
        vals = _get_conta(df_pivot, code, cols_dates)
        if vals.abs().sum() == 0:
            continue
        fig.add_trace(go.Scatter(
            x=cols_dates, y=vals.values,
            name=nome,
            mode="lines+markers",
            line=dict(color=cor, width=2.5),
            marker=dict(size=7, color=cor,
                        line=dict(width=1.5, color="rgba(255,255,255,0.25)")),
            hovertemplate=f"{nome}: %{{y:,.2f}}<extra></extra>",
        ))

    fig.add_hline(y=0, line_dash="dot",
                  line_color="rgba(255,255,255,0.2)", line_width=1)
    apply_theme(fig, height=380, y_title=f"Valor ({scale_option})", x_is_category=True)
    st.plotly_chart(fig, use_container_width=True)

def _render_margens(df_pivot, cols_dates):
    st.subheader("📉 Margens — Evolução Histórica")

    receita = _get_conta(df_pivot, "3.01", cols_dates)
    if receita.abs().sum() == 0:
        st.info("Conta de Receita (3.01) não encontrada para cálculo de margens.")
        return

    config = {
        "Margem Bruta":   ("3.03", PALETA[2]),
        "Margem EBIT":    ("3.05", PALETA[1]),
        "Margem Líquida": ("3.11", PALETA[0]),
    }

    fig = go.Figure()
    for nome, (code, cor) in config.items():
        numerador = _get_conta(df_pivot, code, cols_dates)
        margem = (numerador / receita.replace(0, float("nan"))) * 100
        if margem.isna().all():
            continue
        fig.add_trace(go.Scatter(
            x=cols_dates, y=margem.values,
            name=nome,
            mode="lines+markers",
            line=dict(color=cor, width=2.5),
            marker=dict(size=7, color=cor,
                        line=dict(width=1.5, color="rgba(255,255,255,0.25)")),
            hovertemplate=f"{nome}: %{{y:.1f}}%<extra></extra>",
        ))

    fig.add_hline(y=0, line_dash="dot",
                  line_color="rgba(255,255,255,0.2)", line_width=1)
    apply_theme(fig, height=360, y_title="Margem (%)", y_suffix="%", x_is_category=True)
    st.plotly_chart(fig, use_container_width=True)

def _render_crescimento(df_pivot, cols_dates, empresa):
    receita = _get_conta(df_pivot, "3.01", cols_dates)
    if len(receita) < 2 or receita.abs().sum() == 0:
        return

    var_pct = receita.pct_change().fillna(0)
    val_ini, val_fin = receita.iloc[0], receita.iloc[-1]
    anos = len(receita) - 1
    cagr = (val_fin / val_ini) ** (1 / anos) - 1 if val_ini > 0 and anos > 0 else 0

    st.subheader(f"📊 Crescimento da Receita — CAGR do período: {cagr:.1%}")

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.18,
        row_heights=[0.65, 0.35],
        subplot_titles=("Receita Líquida", "Variação YoY"),
    )

    fig.add_trace(go.Bar(
        x=cols_dates, y=receita.values,
        name="Receita Líquida",
        marker=dict(
            color=receita.values,
            colorscale=[[0, f"rgba(56,189,248,0.5)"], [1, f"rgba(56,189,248,0.9)"]],
            showscale=False, line=dict(width=0),
        ),
        hovertemplate="Receita: %{y:,.2f}<extra></extra>",
    ), row=1, col=1)

    cores_var = [PALETA[2] if v >= 0 else PALETA[7] for v in var_pct.values]
    fig.add_trace(go.Bar(
        x=cols_dates, y=var_pct.values * 100,
        name="Variação YoY (%)",
        marker=dict(color=cores_var, line=dict(width=0)),
        text=[f"{v:.1f}%" if i > 0 else "" for i, v in enumerate(var_pct.values * 100)],
        textposition="outside",
        textfont=dict(color=FONT_COLOR, size=10),
        hovertemplate="YoY: %{y:.1f}%<extra></extra>",
    ), row=2, col=1)

    fig.update_layout(
        plot_bgcolor=BG_TRANSPARENT, paper_bgcolor=BG_TRANSPARENT,
        font=dict(family=FONT_FAMILY, color=FONT_COLOR),
        height=620,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor=LEGEND_BG, bordercolor="rgba(255,255,255,0.10)", borderwidth=1,
            font=dict(color=FONT_COLOR, size=11),
        ),
        hoverlabel=dict(bgcolor="rgba(15,15,30,0.85)", font=dict(color="#F1F5F9")),
        margin=dict(t=80, b=40, l=60, r=40),
        barmode="group",
    )
    for row in [1, 2]:
        fig.update_xaxes(type="category", tickfont=dict(color=FONT_COLOR),
                         gridcolor=GRID_COLOR, linecolor="rgba(255,255,255,0.12)", row=row, col=1)
        fig.update_yaxes(gridcolor=GRID_COLOR, zeroline=True,
                         zerolinecolor=ZERO_LINE_COLOR,
                         tickfont=dict(color=FONT_COLOR), row=row, col=1)
    fig.update_yaxes(ticksuffix="%", row=2, col=1)
    fig.update_annotations(x=0, xanchor="left", font_size=13, yshift=20)

    st.plotly_chart(fig, use_container_width=True)

def render_dre_page():

    with st.sidebar:
        st.header("Filtros — DRE")

        df_empresas = get_companies_demonstrativo("dre")
        if df_empresas.empty:
            st.warning("Tabela DRE indisponível ou sem dados.")
            return

        mapa = dict(zip(df_empresas["LABEL_DROPDOWN"], df_empresas["CNPJ_CIA"]))
        selected_label = st.selectbox(
            "Empresa:", options=df_empresas["LABEL_DROPDOWN"].tolist(),
            key="dre_empresa",
        )
        selected_cnpj = mapa[selected_label]
        st.markdown("---")

        df_dates = get_dates_demonstrativo(selected_cnpj, "dre")
        available_dates = df_dates["DT_REFER"].astype(str).tolist()
        if not available_dates:
            st.error("Sem dados para esta empresa.")
            return

        selected_dates = st.multiselect(
            "Períodos:", options=available_dates,
            default=available_dates[:6] if len(available_dates) >= 6 else available_dates,
            key="dre_datas",
        )
        if not selected_dates:
            st.warning("Selecione pelo menos uma data.")
            return

        st.markdown("---")
        level_selected = st.slider("Nível de Detalhe:", 1, 5, 3, key="dre_level")
        scale_option = st.radio(
            "Escala de Valores:",
            ["Unidade (R$)", "Milhares (Mil)", "Milhões (MM)", "Bilhões (Bi)"],
            index=2, key="dre_scale",
        )
        divisor = {"Unidade (R$)": 1, "Milhares (Mil)": 1_000,
                   "Milhões (MM)": 1_000_000, "Bilhões (Bi)": 1_000_000_000}[scale_option]

    # Cabeçalho
    nome_empresa = selected_label.split(" (")[0]
    st.title(f"📋 DRE — {nome_empresa}")
    st.caption(f"**CNPJ:** {selected_cnpj} | Demonstração do Resultado do Exercício")

    # Carga
    with st.spinner(f"Carregando DRE de {nome_empresa}..."):
        df_raw = get_demonstrativo_filtered(
            selected_cnpj, tuple(selected_dates), level_selected, "dre"
        )
        if df_raw.empty:
            st.info("Nenhum dado encontrado para os filtros selecionados.")
            return

        df_pivot, cols_dates = _pivot_e_datas(df_raw, divisor)

    st.markdown("---")

    # Tabela completa
    _show_table(df_pivot, f"📋 Demonstração do Resultado ({scale_option})", scale_option, cols_dates)
    st.markdown("---")

    # Gráficos
    col_a, col_b = st.columns([1, 1])
    with col_a:
        _render_waterfall(df_pivot, cols_dates, scale_option)
    with col_b:
        _render_margens(df_pivot, cols_dates)

    st.markdown("###")
    _render_evolucao_resultado(df_pivot, cols_dates, scale_option)

    st.markdown("###")
    _render_crescimento(df_pivot, cols_dates, nome_empresa)

    # IA
    st.markdown("---")
    ctx_dre = build_context_dre(df_pivot, cols_dates, nome_empresa, scale_option)
    render_ai_panel(
        contexto=ctx_dre,
        prompt_fn=lambda c: _prompt_dre(c, nome_empresa),
        titulo="🤖 Análise da IA — DRE",
        panel_key=f"dre_{selected_cnpj}",
    )

    # Nota metodológica
    with st.expander("ℹ️ Guia de Contas (padrão CVM DFP)"):
        st.markdown("""
| Código | Conta                                    |
|--------|------------------------------------------|
| 3      | **Resultado** (raiz)                     |
| 3.01   | Receita de Venda / Serviços Líquida      |
| 3.02   | Custo dos Bens / Serviços (CPV/CSP)      |
| 3.03   | **Resultado (Lucro) Bruto**              |
| 3.04   | Despesas / Receitas Operacionais         |
| 3.05   | **EBIT** (Resultado Operacional)         |
| 3.06   | Resultado Financeiro                     |
| 3.07   | Resultado antes dos Tributos (LAIR)      |
| 3.08   | IR e Contribuição Social                 |
| 3.09   | Resultado Líquido — Operações Continuadas|
| 3.11   | **Lucro / Prejuízo do Período**          |
        """)
