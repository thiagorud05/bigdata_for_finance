"""
Demonstração de Fluxo de Caixa (DFC)
Suporta Método Indireto (dfc_mi) e Método Direto (dfc_md).
Segue o mesmo padrão visual do BP/DRE, com gráficos específicos
para análise de fluxo: barras de FCO/FCI/FCF e Free Cash Flow.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from database import get_dates_demonstrativo, get_demonstrativo_filtered
from chart_theme import (
    BG_TRANSPARENT, GRID_COLOR, ZERO_LINE_COLOR,
    FONT_COLOR, FONT_COLOR_TITLE, PALETA, FONT_FAMILY, LEGEND_BG,
    apply_theme, plot_chart,
)
from ai_analyst import (
    render_ai_panel,
    build_context_dfc,
    _prompt_dfc,
)
from glossary import chart_tooltip

def formatar_moeda_br(valor):
    if pd.isna(valor):
        return "-"
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _pivot_e_datas(df_raw, divisor):
    df = df_raw.copy()
    df["VL_CONTA_TRATADO"] = df["VL_CONTA_TRATADO"] / divisor
    df_pivot = df.pivot_table(
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
    return df_pivot[["CD_CONTA", "DS_CONTA"] + cols_dates], cols_dates

def _get_conta(df_pivot, code, cols_dates):
    r = df_pivot[df_pivot["CD_CONTA"] == code]
    if r.empty:
        return pd.Series(0.0, index=cols_dates)
    return r[cols_dates].iloc[0].astype(float)

def _find_root(df_pivot, cols_dates):
    """Detecta o código-raiz do DFC (pode ser 6 ou outro)."""
    candidates = ["6", "6.01"]
    for c in candidates:
        r = df_pivot[df_pivot["CD_CONTA"] == c]
        if not r.empty and r[cols_dates].abs().sum().sum() > 0:
            return c
    # fallback: pega a conta com menor número de dígitos
    min_len = df_pivot["CD_CONTA"].str.len().min()
    rows = df_pivot[df_pivot["CD_CONTA"].str.len() == min_len]
    return rows.iloc[0]["CD_CONTA"] if not rows.empty else None

def _show_table(df_input, titulo, cols_dates):
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

def _render_fluxos(df_pivot, cols_dates, scale_option):
    st.subheader("Fluxos de Caixa por Atividade", help=chart_tooltip("fluxos_dfc"))

    # Tenta identificar as três atividades principais
    config_fluxos = [
        ("6.01", "🟢 FCO — Operacional", PALETA[2]),
        ("6.02", "🔴 FCI — Investimento", PALETA[7]),
        ("6.03", "🔵 FCF — Financiamento", PALETA[1]),
    ]

    fig = go.Figure()
    encontrou = False
    for code, nome, cor in config_fluxos:
        vals = _get_conta(df_pivot, code, cols_dates)
        if vals.abs().sum() == 0:
            continue
        encontrou = True
        fig.add_trace(go.Bar(
            x=cols_dates, y=vals.values,
            name=nome,
            marker=dict(color=cor, opacity=0.85, line=dict(width=0)),
            hovertemplate=f"{nome}: %{{y:,.2f}}<extra></extra>",
        ))

    if not encontrou:
        st.info("Contas 6.01 / 6.02 / 6.03 não encontradas. "
                "Verifique se o nível de detalhe inclui subcontas.")
        return

    fig.add_hline(y=0, line_dash="dot",
                  line_color="rgba(255,255,255,0.2)", line_width=1)
    fig.update_layout(barmode="group")
    apply_theme(fig, height=400, y_title=f"Valor ({scale_option})", x_is_category=True)
    plot_chart(fig)

def _render_fcf(df_pivot, cols_dates, scale_option):
    st.subheader("Free Cash Flow (FCO − |FCI|)", help=chart_tooltip("fcf_dfc"))

    fco = _get_conta(df_pivot, "6.01", cols_dates)
    fci = _get_conta(df_pivot, "6.02", cols_dates)

    if fco.abs().sum() == 0:
        st.info("FCO (6.01) não encontrado para calcular Free Cash Flow.")
        return

    fcf = fco + fci   # FCI geralmente é negativo, então soma é subtração

    cores = [PALETA[2] if v >= 0 else PALETA[7] for v in fcf.values]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cols_dates, y=fco.values,
        name="FCO — Operacional",
        marker=dict(color=PALETA[2], opacity=0.70, line=dict(width=0)),
        hovertemplate="FCO: %{y:,.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=cols_dates, y=fcf.values,
        name="Free Cash Flow",
        mode="lines+markers+text",
        line=dict(color=PALETA[0], width=3),
        marker=dict(size=9, color=PALETA[0],
                    line=dict(width=1.5, color="rgba(255,255,255,0.3)")),
        text=[formatar_moeda_br(v) for v in fcf.values],
        textposition="top center",
        textfont=dict(size=10, color=PALETA[0]),
        hovertemplate="FCF: %{y:,.2f}<extra></extra>",
    ))

    fig.add_hline(y=0, line_dash="dot",
                  line_color="rgba(255,255,255,0.2)", line_width=1)
    apply_theme(fig, height=380, y_title=f"Valor ({scale_option})", x_is_category=True)
    plot_chart(fig)

def _render_cascata_caixa(df_pivot, cols_dates, scale_option):
    st.subheader("Composição da Variação de Caixa (último período)", help=chart_tooltip("cascata_caixa_dfc"))

    dt_ref = cols_dates[-1]
    config = [
        ("6.01", "FCO Operacional"),
        ("6.02", "FCI Investimento"),
        ("6.03", "FCF Financiamento"),
    ]

    labels, vals, medidas = [], [], []
    for code, label in config:
        r = df_pivot[df_pivot["CD_CONTA"] == code]
        if r.empty:
            continue
        v = float(r[dt_ref].iloc[0])
        labels.append(label)
        vals.append(v)
        medidas.append("relative")

    if not labels:
        st.info("Contas de fluxo (6.01/6.02/6.03) não encontradas.")
        return

    # Soma como total
    labels.append("Variação Líquida")
    vals.append(sum(vals))
    medidas.append("total")

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=medidas,
        x=labels,
        y=vals,
        text=[formatar_moeda_br(v) for v in vals],
        textposition="outside",
        textfont=dict(color=FONT_COLOR, size=10),
        connector=dict(line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot")),
        increasing=dict(marker_color=PALETA[2]),
        decreasing=dict(marker_color=PALETA[7]),
        totals=dict(marker_color=PALETA[0]),
        hovertemplate="%{x}: %{text}<extra></extra>",
    ))

    apply_theme(fig, height=380, y_title=f"Valor ({scale_option})", x_is_category=True)
    plot_chart(fig)
    st.caption(f"📅 Período de referência: **{dt_ref}**")

def _render_caixa_acumulado(df_pivot, cols_dates, scale_option):
    fco = _get_conta(df_pivot, "6.01", cols_dates)
    if fco.abs().sum() == 0 or len(cols_dates) < 2:
        return

    st.subheader("FCO Acumulado no Período Analisado", help=chart_tooltip("caixa_acumulado_dfc"))

    fco_cum = fco.cumsum()
    cores = [PALETA[2] if v >= 0 else PALETA[7] for v in fco_cum.values]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cols_dates, y=fco.values,
        name="FCO (período)",
        marker=dict(color=PALETA[1], opacity=0.60, line=dict(width=0)),
        hovertemplate="FCO: %{y:,.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=cols_dates, y=fco_cum.values,
        name="FCO Acumulado",
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(144,202,249,0.18)",
        line=dict(color=PALETA[0], width=3),
        marker=dict(size=8, color=PALETA[0],
                    line=dict(width=1.5, color="rgba(255,255,255,0.3)")),
        hovertemplate="Acumulado: %{y:,.2f}<extra></extra>",
    ))

    fig.add_hline(y=0, line_dash="dot",
                  line_color="rgba(255,255,255,0.2)", line_width=1)
    apply_theme(fig, height=360, y_title=f"Valor ({scale_option})", x_is_category=True)
    plot_chart(fig)

def _render_bolha_fco_fci(df_pivot, cols_dates, scale_option):
    """Scatter: FCO (x) vs FCI (y), tamanho = variação absoluta total."""
    st.subheader("FCO vs FCI — Dispersão Temporal", help=chart_tooltip("bolha_fco_fci_dfc"))

    fco = _get_conta(df_pivot, "6.01", cols_dates)
    fci = _get_conta(df_pivot, "6.02", cols_dates)

    if fco.abs().sum() == 0 or fci.abs().sum() == 0:
        st.info("FCO ou FCI não disponíveis para o gráfico de dispersão.")
        return

    fcf = (fco + fci).abs()
    cores_pts = [PALETA[2] if (fco.iloc[i] > 0 and fci.iloc[i] < 0) else
                 PALETA[7] if fco.iloc[i] < 0 else PALETA[0]
                 for i in range(len(cols_dates))]

    fig = go.Figure(go.Scatter(
        x=fco.values, y=fci.values,
        mode="markers+text",
        text=cols_dates,
        textposition="top center",
        textfont=dict(size=9, color=FONT_COLOR),
        marker=dict(
            size=[max(12, min(50, abs(v) / max(fcf.max(), 1) * 50)) for v in fcf.values],
            color=cores_pts,
            opacity=0.80,
            line=dict(width=1.5, color="rgba(19,41,61,0.15)"),
        ),
        hovertemplate="%{text}<br>FCO: %{x:,.2f}<br>FCI: %{y:,.2f}<extra></extra>",
    ))

    fig.add_hline(y=0, line_dash="dot", line_color=ZERO_LINE_COLOR, line_width=1)
    fig.add_vline(x=0, line_dash="dot", line_color=ZERO_LINE_COLOR, line_width=1)
    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT, plot_bgcolor=BG_TRANSPARENT,
        font=dict(family=FONT_FAMILY, color=FONT_COLOR), height=380,
        xaxis=dict(title_text=f"FCO ({scale_option})", title_font=dict(color=FONT_COLOR),
                   tickfont=dict(color=FONT_COLOR), gridcolor=GRID_COLOR, zeroline=True),
        yaxis=dict(title_text=f"FCI ({scale_option})", title_font=dict(color=FONT_COLOR),
                   tickfont=dict(color=FONT_COLOR), gridcolor=GRID_COLOR, zeroline=True),
        margin=dict(t=20, b=50, l=60, r=20),
        hoverlabel=dict(bgcolor="rgba(19,41,61,0.92)", font=dict(color="#E8F1F2")),
    )
    plot_chart(fig)
    st.caption("🟢 FCO+ / FCI− (saudável) | 🔴 FCO− (alerta) | tamanho = magnitude do FCF")


def render_dfc_page():

    selected_cnpj = st.session_state.get("global_cnpj")
    selected_label = st.session_state.get("global_label", "")
    if not selected_cnpj:
        st.warning("Selecione uma empresa na barra lateral.")
        return

    tabela_alias = "dfc"   # única tabela disponível no banco
    with st.sidebar:
        df_dates = get_dates_demonstrativo(selected_cnpj, tabela_alias)
        available_dates = df_dates["DT_REFER"].astype(str).tolist()
        if not available_dates:
            st.error("Sem dados para esta empresa.")
            return

        selected_dates = st.multiselect(
            "Períodos:", options=available_dates,
            default=available_dates[:6] if len(available_dates) >= 6 else available_dates,
            key="dfc_datas",
        )
        if not selected_dates:
            st.warning("Selecione pelo menos uma data.")
            return

        st.markdown("---")
        level_selected = st.slider("Nível de Detalhe:", 1, 5, 2, key="dfc_level")
        scale_option = st.radio(
            "Escala de Valores:",
            ["Unidade (R$)", "Milhares (Mil)", "Milhões (MM)", "Bilhões (Bi)"],
            index=2, key="dfc_scale",
        )
        divisor = {"Unidade (R$)": 1, "Milhares (Mil)": 1_000,
                   "Milhões (MM)": 1_000_000, "Bilhões (Bi)": 1_000_000_000}[scale_option]

    # Cabeçalho
    nome_empresa = selected_label.split(" (")[0]
    st.title(f"DFC — {nome_empresa}")
    st.caption(
        f"**CNPJ:** {selected_cnpj} | "
        "Demonstração dos Fluxos de Caixa"
    )


    # Carga
    with st.spinner(f"Carregando DFC de {nome_empresa}..."):
        df_raw = get_demonstrativo_filtered(
            selected_cnpj, tuple(selected_dates), level_selected, tabela_alias
        )
        if df_raw.empty:
            st.info("Nenhum dado encontrado para os filtros selecionados.")
            return

        df_pivot, cols_dates = _pivot_e_datas(df_raw, divisor)

    st.markdown("---")

    # Tabela completa
    _show_table(df_pivot, f"Demonstração dos Fluxos de Caixa ({scale_option})", cols_dates)
    st.markdown("---")

    # Gráficos principais
    col_a, col_b = st.columns(2)
    with col_a:
        _render_fluxos(df_pivot, cols_dates, scale_option)
    with col_b:
        _render_cascata_caixa(df_pivot, cols_dates, scale_option)

    st.markdown("###")

    col_c, col_d = st.columns(2)
    with col_c:
        _render_fcf(df_pivot, cols_dates, scale_option)
    with col_d:
        _render_caixa_acumulado(df_pivot, cols_dates, scale_option)

    st.markdown("###")
    _render_bolha_fco_fci(df_pivot, cols_dates, scale_option)

    # IA
    st.markdown("---")
    ctx_dfc = build_context_dfc(df_pivot, cols_dates, nome_empresa, scale_option)
    render_ai_panel(
        contexto=ctx_dfc,
        prompt_fn=lambda c: _prompt_dfc(c, nome_empresa),
        titulo="Análise da IA — DFC",
        panel_key=f"dfc_{selected_cnpj}",
    )

    # Nota metodológica
    with st.expander("ℹ️ Guia de Contas — DFC (padrão CVM DFP)"):
        st.markdown("""
| Código | Conta                                              |
|--------|----------------------------------------------------|
| 6      | **Variação Líquida de Caixa** (raiz)               |
| 6.01   | **FCO** — Caixa das Atividades Operacionais        |
| 6.02   | **FCI** — Caixa das Atividades de Investimento     |
| 6.03   | **FCF** — Caixa das Atividades de Financiamento    |

**Free Cash Flow (FCF)** = FCO + FCI  
_(FCI costuma ser negativo, então a soma equivale a uma subtração)_
        """)

