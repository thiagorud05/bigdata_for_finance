import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from database import (
    get_companies_indicadores,
    get_indicadores_data,
    get_sectors_list,
    get_sector_benchmark,
    get_all_sectors_benchmark,
    get_sector_time_series,
)
from chart_theme import (
    apply_theme, apply_polar_theme, apply_heatmap_theme,
    bar_trace, line_trace, scatter_polar_trace,
    PALETA, CORES, FONT_COLOR, FONT_COLOR_TITLE,
    BG_TRANSPARENT, GRID_COLOR, ZERO_LINE_COLOR,
    plot_chart,
)
from ai_analyst import (
    render_ai_panel,
    build_context_comparativo_empresas,
    build_context_vs_setor,
    build_context_vs_todos_setores,
    _prompt_comparativo,
    _prompt_vs_todos_setores,
)
from glossary import tooltip

GRUPOS_INDICADORES = {
    "Rentabilidade": {
        "MARGEM_BRUTA":   ("Margem Bruta",    "pct", True),
        "MARGEM_EBIT":    ("Margem EBIT",      "pct", True),
        "MARGEM_LIQUIDA": ("Margem Líquida",   "pct", True),
        "ROA":            ("ROA",              "pct", True),
        "ROE":            ("ROE",              "pct", True),
    },
    "Liquidez": {
        "LIQUIDEZ_CORRENTE":  ("Liq. Corrente",  "num", True),
        "LIQUIDEZ_SECA":      ("Liq. Seca",      "num", True),
        "LIQUIDEZ_IMEDIATA":  ("Liq. Imediata",  "num", True),
        "LIQUIDEZ_GERAL":     ("Liq. Geral",     "num", True),
    },
    "Endividamento": {
        "ENDIVIDAMENTO_GERAL":      ("Endividamento Geral",  "pct", False),
        "GRAU_ENDIVIDAMENTO":       ("Grau Endividamento",   "num", False),
        "COMPOSICAO_ENDIVIDAMENTO": ("Comp. Endividamento",  "pct", False),
    },
    "Ciclos": {
        "PMRV":             ("PMRV (dias)",      "dias", False),
        "PME":              ("PME (dias)",        "dias", False),
        "PMPF":             ("PMPF (dias)",       "dias", True),
        "CICLO_OPERACIONAL":("Ciclo Operacional", "dias", False),
        "CICLO_FINANCEIRO": ("Ciclo Financeiro",  "dias", False),
    },
}

TODOS_INDICADORES = {k: v for grp in GRUPOS_INDICADORES.values() for k, v in grp.items()}

INDICADORES_RADAR = [
    "MARGEM_BRUTA","MARGEM_LIQUIDA","ROE","ROA",
    "LIQUIDEZ_CORRENTE","LIQUIDEZ_SECA","ENDIVIDAMENTO_GERAL",
]

def fmt_val(val, tipo):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "—"
    if tipo == "pct":
        return f"{val * 100:.1f}%"
    if tipo == "dias":
        return f"{val:.0f} d"
    return f"{val:.2f}"

def safe_float(row, col):
    v = row.get(col, None)
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return float(v)

def _mult(tipo): return 100 if tipo == "pct" else 1

def _render_radar(dfs: dict, cols: list):
    labels = [TODOS_INDICADORES[c][0] for c in cols if c in TODOS_INDICADORES]
    cols_ok = [c for c in cols if c in TODOS_INDICADORES]

    maximos = {}
    for col in cols_ok:
        raw = [abs(float(row.get(col))) for row in dfs.values()
               if row.get(col) is not None and not np.isnan(float(row.get(col)))]
        maximos[col] = max(raw) if raw else 1.0

    fig = go.Figure()
    for i, (nome, row) in enumerate(dfs.items()):
        cor = PALETA[i % len(PALETA)]
        vals = []
        for col in cols_ok:
            v = safe_float(row, col)
            mxv = maximos.get(col, 1.0) or 1.0
            vals.append(min(abs(v) / mxv, 1.0) if v is not None else 0.0)

        theta = labels + [labels[0]]
        r     = vals  + [vals[0]]
        rv = int(cor[1:3], 16); gv = int(cor[3:5], 16); bv = int(cor[5:7], 16)

        fig.add_trace(go.Scatterpolar(
            r=r, theta=theta, fill="toself", name=nome,
            line=dict(color=cor, width=2.2),
            fillcolor=f"rgba({rv},{gv},{bv},0.12)",
            marker=dict(size=5, color=cor),
        ))

    apply_polar_theme(fig, height=420)
    plot_chart(fig)
    st.caption("⚠️ Valores normalizados pelo máximo do grupo comparado — não representa percentil.")

def _render_scorecard(emp_row, bench_row):
    cols_score = [
        ("MARGEM_LIQUIDA",     "Margem Líquida", "pct", True),
        ("ROE",                "ROE",            "pct", True),
        ("LIQUIDEZ_CORRENTE",  "Liq. Corrente",  "num", True),
        ("ENDIVIDAMENTO_GERAL","Endividamento",  "pct", False),
        ("MARGEM_BRUTA",       "Margem Bruta",   "pct", True),
        ("ROA",                "ROA",            "pct", True),
    ]
    colunas = st.columns(len(cols_score))
    for i, (col, label_txt, tipo, maior_melhor) in enumerate(cols_score):
        v_emp   = safe_float(emp_row, col)
        v_bench = safe_float(bench_row, col)
        if v_emp is None:
            continue

        delta_str = None
        delta_color = "normal"
        if v_bench and v_bench != 0:
            diff = v_emp - v_bench
            delta_str = fmt_val(diff, tipo)
            acima = diff > 0
            delta_color = "normal" if (maior_melhor == acima) else "inverse"

        tip = tooltip(col)
        tip_full = (tip + "\n\n" if tip else "") + f"⏺ Mediana do setor: {fmt_val(v_bench, tipo)}"

        with colunas[i]:
            st.metric(label=label_txt, value=fmt_val(v_emp, tipo),
                      delta=delta_str, delta_color=delta_color,
                      help=tip_full)

def _render_evolucao_vs_setor(cnpj, nome_empresa, setor):
    df_emp   = get_indicadores_data(cnpj)
    df_setor = get_sector_time_series(setor)

    fig = go.Figure()
    if not df_emp.empty and "MARGEM_LIQUIDA" in df_emp.columns:
        de = df_emp.dropna(subset=["MARGEM_LIQUIDA"]).sort_values("DT_REFER")
        fig.add_trace(go.Scatter(
            x=de["DT_REFER"].astype(str), y=de["MARGEM_LIQUIDA"] * 100,
            name=nome_empresa, mode="lines+markers",
            line=dict(color=PALETA[0], width=3),
            marker=dict(size=8, color=PALETA[0],
                        line=dict(width=1.5, color="rgba(255,255,255,0.3)")),
            fill="tozeroy", fillcolor="rgba(144,202,249,0.18)",
            hovertemplate=f"{nome_empresa}: %{{y:.1f}}%<extra></extra>",
        ))

    if not df_setor.empty and "MARGEM_LIQUIDA" in df_setor.columns:
        ds = df_setor.dropna(subset=["MARGEM_LIQUIDA"]).sort_values("DT_REFER")
        fig.add_trace(go.Scatter(
            x=ds["DT_REFER"].astype(str), y=ds["MARGEM_LIQUIDA"] * 100,
            name=f"⌀ {setor}", mode="lines+markers",
            line=dict(color=PALETA[1], width=2, dash="dash"),
            marker=dict(size=6, color=PALETA[1], symbol="diamond",
                        line=dict(width=1, color="rgba(255,255,255,0.25)")),
            hovertemplate=f"Mediana {setor}: %{{y:.1f}}%<extra></extra>",
        ))

    fig.add_hline(y=0, line_dash="dot",
                  line_color="rgba(255,255,255,0.2)", line_width=1)
    apply_theme(fig, height=360, y_title="Margem Líquida (%)", y_suffix="%",
                x_is_category=True)
    plot_chart(fig)

def _render_heatmap_grupo(df_hm, cols, labels, tipos, nome_empresa, tab_key):
    """Renderiza um heatmap para um subconjunto de colunas (um grupo de indicadores)."""
    # Z-Score por coluna — negado quando menor é melhor
    z_cols = []
    for col in cols:
        col_data = pd.to_numeric(df_hm[col], errors="coerce")
        mn, sd = col_data.mean(), col_data.std()
        z = ((col_data - mn) / sd).fillna(0) if sd and not np.isnan(sd) else pd.Series([0.0]*len(df_hm))
        if not TODOS_INDICADORES[col][2]:
            z = -z
        z_cols.append(z.tolist())

    z_t   = list(map(list, zip(*z_cols)))
    text_m = [[fmt_val(row.get(c), t) for c, t in zip(cols, tipos)]
               for _, row in df_hm.iterrows()]

    fig = go.Figure(go.Heatmap(
        z=z_t, x=labels, y=df_hm["SETOR"].tolist(),
        text=text_m, texttemplate="%{text}",
        textfont=dict(size=10, color="#13293D"),
        colorscale="RdYlGn", zmid=0,
        colorbar=dict(
            title=dict(text="Z-Score", font=dict(color=FONT_COLOR, size=11)),
            tickfont=dict(color=FONT_COLOR), thickness=12, len=0.6,
        ),
        hovertemplate="<b>%{y}</b><br>%{x}: %{text}<extra></extra>",
    ))

    # Destaque linha da empresa
    fig.add_shape(
        type="rect", x0=-0.5, x1=len(labels)-0.5, y0=-0.5, y1=0.5,
        line=dict(color=PALETA[0], width=2.5),
        xref="x", yref="y",
    )

    altura = max(350, len(df_hm) * 34 + 80)
    apply_heatmap_theme(fig, height=altura)
    # margem esquerda menor quando há poucas colunas (leitura mobile)
    fig.update_layout(margin=dict(t=20, b=60, l=160, r=40))
    plot_chart(fig, key=f"hm_{tab_key}")


def _render_heatmap_setores(df_all_bench, emp_row, nome_empresa, setor_empresa):
    # Monta df base com empresa no topo
    all_cols = [c for c in TODOS_INDICADORES if c in df_all_bench.columns]
    df_setores = df_all_bench[["SETOR"] + all_cols].dropna(subset=["SETOR"]).copy()
    emp_row_dict = {"SETOR": f"★ {nome_empresa}"}
    for c in all_cols:
        v = emp_row.get(c, None)
        emp_row_dict[c] = float(v) if v is not None and not pd.isna(v) else None
    df_hm = pd.concat([pd.DataFrame([emp_row_dict]), df_setores], ignore_index=True)

    # Uma aba por grupo de indicadores + aba final com todos
    tab_labels = list(GRUPOS_INDICADORES.keys()) + ["Todos"]
    tabs = st.tabs(tab_labels)

    for tab, (grupo, indicadores) in zip(tabs, GRUPOS_INDICADORES.items()):
        cols   = [c for c in indicadores if c in all_cols]
        labels = [indicadores[c][0] for c in cols]
        tipos  = [indicadores[c][1] for c in cols]
        with tab:
            if cols:
                _render_heatmap_grupo(df_hm, cols, labels, tipos, nome_empresa, grupo)
            else:
                st.info("Dados não disponíveis para este grupo.")

    with tabs[-1]:
        all_labels = [TODOS_INDICADORES[c][0] for c in all_cols]
        all_tipos  = [TODOS_INDICADORES[c][1] for c in all_cols]
        st.caption("📱 Recomendado usar na horizontal ou no computador para visualizar todos os indicadores.")
        _render_heatmap_grupo(df_hm, all_cols, all_labels, all_tipos, nome_empresa, "todos")

def render_empresa_vs_empresa(empresas_selecionadas: dict, data_ref: str):
    st.subheader("Empresa vs Empresa")
    st.caption(f"Período de referência: **{data_ref}**")

    dfs = {}
    for cnpj, nome in empresas_selecionadas.items():
        df = get_indicadores_data(cnpj)
        linha = df[df["DT_REFER"].astype(str) == data_ref]
        if not linha.empty:
            dfs[nome] = linha.iloc[0]

    if not dfs:
        st.warning("Nenhum dado encontrado para as empresas e data selecionadas.")
        return

    st.markdown("#### Radar de Indicadores")
    _render_radar(dfs, INDICADORES_RADAR)
    st.markdown("---")

    for grupo, indicadores in GRUPOS_INDICADORES.items():
        st.markdown(f"#### {grupo}")
        cols_grp   = list(indicadores.keys())
        labels_grp = [indicadores[c][0] for c in cols_grp]
        tipos_grp  = [indicadores[c][1] for c in cols_grp]

        fig = go.Figure()
        for i, (nome, row) in enumerate(dfs.items()):
            cor = PALETA[i % len(PALETA)]
            vals  = [safe_float(row, c) for c in cols_grp]
            vals_plot = [v * _mult(t) if v is not None else None
                         for v, t in zip(vals, tipos_grp)]
            textos = [fmt_val(v, t) for v, t in zip(vals, tipos_grp)]

            fig.add_trace(go.Bar(
                name=nome, x=labels_grp, y=vals_plot,
                text=textos, textposition="outside",
                textfont=dict(color=FONT_COLOR, size=10),
                marker=dict(color=cor, opacity=0.85, line=dict(width=0)),
                hovertemplate=f"<b>{nome}</b><br>%{{x}}: %{{text}}<extra></extra>",
            ))

        fig.update_layout(barmode="group")
        apply_theme(fig, height=320, x_is_category=True)
        plot_chart(fig)

    # Evolução temporal — Margem Líquida
    st.markdown("#### Evolução Temporal — Margem Líquida")
    fig_ev = go.Figure()
    for i, (cnpj, nome) in enumerate(empresas_selecionadas.items()):
        df = get_indicadores_data(cnpj)
        if df.empty or "MARGEM_LIQUIDA" not in df.columns:
            continue
        de = df.dropna(subset=["MARGEM_LIQUIDA"]).sort_values("DT_REFER")
        cor = PALETA[i % len(PALETA)]
        fig_ev.add_trace(go.Scatter(
            x=de["DT_REFER"].astype(str), y=de["MARGEM_LIQUIDA"] * 100,
            name=nome, mode="lines+markers",
            line=dict(color=cor, width=2.5),
            marker=dict(size=7, color=cor,
                        line=dict(width=1.5, color="rgba(255,255,255,0.25)")),
            hovertemplate=f"{nome}: %{{y:.1f}}%<extra></extra>",
        ))
    fig_ev.add_hline(y=0, line_dash="dot",
                     line_color="rgba(255,255,255,0.2)", line_width=1)
    apply_theme(fig_ev, height=360, y_title="Margem Líquida (%)", y_suffix="%",
                x_is_category=True)
    plot_chart(fig_ev)

    with st.expander("📋 Tabela Comparativa"):
        rows = [{"Indicador": TODOS_INDICADORES[c][0],
                 "📖": tooltip(c) or "",
                 **{nome: fmt_val(safe_float(row, c), TODOS_INDICADORES[c][1])
                    for nome, row in dfs.items()}}
                for c in TODOS_INDICADORES]
        df_tab = pd.DataFrame(rows)
        col_cfg_tab = {
            "Indicador": st.column_config.TextColumn("Indicador", width="medium"),
            "📖": st.column_config.TextColumn("Descrição", width="large", help="Fórmula e interpretação do indicador"),
            **{nome: st.column_config.TextColumn(nome, width="small") for nome in dfs},
        }
        st.dataframe(df_tab, hide_index=True, use_container_width=True, column_config=col_cfg_tab)


    # IA
    st.markdown("---")
    ctx = build_context_comparativo_empresas(dfs, data_ref)
    render_ai_panel(
        contexto=ctx,
        prompt_fn=lambda c: _prompt_comparativo(c, "Empresa vs Empresa"),
        titulo="Análise da IA — Comparativo entre Empresas",
        panel_key="cmp_emp_emp",
    )


def render_empresa_vs_setor(cnpj: str, nome_empresa: str, setor: str, data_ref: str):
    st.subheader(f"{nome_empresa} × Setor: {setor}")
    st.caption(f"Período: **{data_ref}** | Benchmark: **mediana do setor**")

    df_emp   = get_indicadores_data(cnpj)
    df_emp_dt = df_emp[df_emp["DT_REFER"].astype(str) == data_ref]
    df_bench = get_sector_benchmark(setor, data_ref)
    df_bench_q = get_sector_benchmark(setor, data_ref, incluir_quartis=True)

    if df_emp_dt.empty:
        st.warning(f"Sem dados para {nome_empresa} em {data_ref}."); return
    if df_bench.empty:
        st.warning(f"Sem benchmark para '{setor}' em {data_ref}."); return

    emp_row   = df_emp_dt.iloc[0]
    bench_row = df_bench.iloc[0]

    st.markdown("#### Radar — Empresa vs Mediana do Setor")
    _render_radar({nome_empresa: emp_row, f"⌀ Mediana {setor}": bench_row}, INDICADORES_RADAR)
    st.markdown("---")

    for grupo, indicadores in GRUPOS_INDICADORES.items():
        st.markdown(f"#### {grupo}")
        cols_grp   = list(indicadores.keys())
        labels_grp = [indicadores[c][0] for c in cols_grp]
        tipos_grp  = [indicadores[c][1] for c in cols_grp]

        def sv(row, col, tipo):
            v = safe_float(row, col)
            return v * _mult(tipo) if v is not None else None

        vals_emp   = [sv(emp_row, c, t)   for c, t in zip(cols_grp, tipos_grp)]
        vals_bench = [sv(bench_row, c, t) for c, t in zip(cols_grp, tipos_grp)]
        textos_emp   = [fmt_val(safe_float(emp_row, c), t)   for c, t in zip(cols_grp, tipos_grp)]
        textos_bench = [fmt_val(safe_float(bench_row, c), t) for c, t in zip(cols_grp, tipos_grp)]

        fig = go.Figure()

        # Banda P25–P75
        if not df_bench_q.empty:
            for j, (col, tipo) in enumerate(zip(cols_grp, tipos_grp)):
                p25v = safe_float(df_bench_q.iloc[0], f"{col}_P25")
                p75v = safe_float(df_bench_q.iloc[0], f"{col}_P75")
                if p25v is not None and p75v is not None:
                    m = _mult(tipo)
                    fig.add_shape(
                        type="rect",
                        x0=j - 0.44, x1=j + 0.44,
                        y0=p25v * m, y1=p75v * m,
                        fillcolor="rgba(255,255,255,0.06)",
                        line=dict(color="rgba(255,255,255,0.12)", width=1),
                        xref="x", yref="y",
                    )

        fig.add_trace(go.Bar(
            name=nome_empresa, x=labels_grp, y=vals_emp,
            text=textos_emp, textposition="outside",
            textfont=dict(color=FONT_COLOR, size=10),
            marker=dict(color=PALETA[0], opacity=0.88, line=dict(width=0)),
            hovertemplate=f"<b>{nome_empresa}</b><br>%{{x}}: %{{text}}<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            name=f"⌀ {setor}", x=labels_grp, y=vals_bench,
            text=textos_bench, textposition="outside",
            textfont=dict(color=FONT_COLOR, size=10),
            marker=dict(color=PALETA[1], opacity=0.65, line=dict(width=0)),
            hovertemplate=f"<b>Mediana {setor}</b><br>%{{x}}: %{{text}}<extra></extra>",
        ))

        fig.update_layout(barmode="group")
        apply_theme(fig, height=320, x_is_category=True)
        plot_chart(fig)

    st.markdown("#### Posicionamento vs Mediana")
    _render_scorecard(emp_row, bench_row)

    # IA
    st.markdown("---")
    ctx = build_context_vs_setor(emp_row, bench_row, nome_empresa, setor, data_ref)
    render_ai_panel(
        contexto=ctx,
        prompt_fn=lambda c: _prompt_comparativo(c, f"Empresa vs Setor ({setor})"),
        titulo="Análise da IA — Empresa vs Setor",
        panel_key=f"cmp_emp_setor_{setor}",
    )


def render_empresa_vs_todos_setores(cnpj: str, nome_empresa: str, data_ref: str):
    st.subheader(f"{nome_empresa} × Todos os Setores")
    st.caption(f"Período: **{data_ref}** | Benchmark: mediana por setor")

    df_emp    = get_indicadores_data(cnpj)
    df_emp_dt = df_emp[df_emp["DT_REFER"].astype(str) == data_ref]
    df_all    = get_all_sectors_benchmark(data_ref)

    if df_emp_dt.empty:
        st.warning(f"Sem dados para {nome_empresa} em {data_ref}."); return
    if df_all.empty:
        st.warning(f"Sem benchmark de setores para {data_ref}."); return

    emp_row = df_emp_dt.iloc[0]
    setor_empresa = emp_row.get("SETOR", "—")

    st.markdown("#### Heatmap — Indicadores por Setor")
    st.markdown(
        '<div class="mobile-heatmap-hint">'
        '📱 <strong>Dica:</strong> Gire o celular na horizontal ou acesse pelo computador '
        'para melhor visualização do heatmap.'
        '</div>',
        unsafe_allow_html=True,
    )
    _render_heatmap_setores(df_all, emp_row, nome_empresa, setor_empresa)
    st.markdown("---")

    st.markdown("#### Ranking por Indicador")
    ind_opcoes = {TODOS_INDICADORES[k][0]: k for k in TODOS_INDICADORES
                  if k in df_all.columns}
    ind_label = st.selectbox(
        "Indicador:", options=list(ind_opcoes),
        index=list(ind_opcoes).index("Margem Líquida") if "Margem Líquida" in ind_opcoes else 0,
        key="rank_ind_selector",
    )
    col_sel  = ind_opcoes[ind_label]
    tipo_sel = TODOS_INDICADORES[col_sel][1]
    maior_m  = TODOS_INDICADORES[col_sel][2]
    mult     = _mult(tipo_sel)

    df_rank = df_all[["SETOR", col_sel]].dropna().sort_values(
        col_sel, ascending=not maior_m
    ).reset_index(drop=True)

    cores_bar = [PALETA[0] if s == setor_empresa else PALETA[1]
                 for s in df_rank["SETOR"]]
    textos_r  = [fmt_val(v, tipo_sel) for v in df_rank[col_sel]]

    fig_r = go.Figure(go.Bar(
        x=df_rank["SETOR"], y=df_rank[col_sel] * mult,
        text=textos_r, textposition="outside",
        textfont=dict(color=FONT_COLOR, size=10),
        marker=dict(color=cores_bar, opacity=0.85, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>" + ind_label + ": %{text}<extra></extra>",
    ))

    val_emp = safe_float(emp_row, col_sel)
    if val_emp is not None:
        fig_r.add_hline(
            y=val_emp * mult,
            line_dash="dash", line_color=PALETA[0], line_width=2,
            annotation_text=f"  {nome_empresa}: {fmt_val(val_emp, tipo_sel)}",
            annotation_position="top right",
            annotation_font=dict(color=PALETA[0], size=11),
        )

    apply_theme(fig_r, height=420, y_title=ind_label, x_is_category=True)
    fig_r.update_layout(margin=dict(b=130))
    fig_r.update_xaxes(tickangle=-35)
    plot_chart(fig_r)

    with st.expander("📋 Tabela Completa por Setor"):
        colunas_exib = ["SETOR"] + [c for c in TODOS_INDICADORES if c in df_all.columns]
        df_exib = df_all[colunas_exib].copy()
        for c in colunas_exib[1:]:
            t = TODOS_INDICADORES[c][1]
            df_exib[c] = df_exib[c].apply(lambda v: fmt_val(v, t))
        df_exib.columns = ["Setor"] + [TODOS_INDICADORES[c][0] for c in colunas_exib[1:]]
        st.dataframe(df_exib, hide_index=True, use_container_width=True)

    # IA
    st.markdown("---")
    ctx = build_context_vs_todos_setores(df_all, emp_row, nome_empresa, data_ref)
    render_ai_panel(
        contexto=ctx,
        prompt_fn=lambda c: _prompt_vs_todos_setores(c, nome_empresa),
        titulo="Análise da IA — Empresa vs Todos os Setores",
        panel_key=f"cmp_global_{cnpj}",
    )


def render_comparativo_page():

    with st.sidebar:
        st.header("Filtros — Comparativo")

        modo = st.radio(
            "Modo de Comparação:",
            options=[
                "🏢 Empresa vs Empresa",
                "🏭 Empresa vs Setor",
                "🌐 Empresa vs Todos os Setores",
            ],
            key="modo_comparativo",
        )
        st.markdown("---")

        df_empresas = get_companies_indicadores()
        if df_empresas.empty:
            st.warning("Base de indicadores indisponível.")
            return

        mapa_emp = dict(zip(df_empresas["LABEL"], df_empresas["CNPJ_CIA"]))
        setores_disp = get_sectors_list()

        # ── MODO 1 ──────────────────────────────────────────────────────────
        if modo == "🏢 Empresa vs Empresa":
            empresas_sel = st.multiselect(
                "Empresas (2 a 5):", options=df_empresas["LABEL"].tolist(),
                max_selections=5, key="cmp_multi",
            )
            if len(empresas_sel) < 2:
                st.info("Selecione ao menos 2 empresas.")
                st.stop()

            empresas_selecionadas = {mapa_emp[l]: l.split(" (")[0] for l in empresas_sel}
            datas_all = None
            for cnpj in empresas_selecionadas:
                dts = set(get_indicadores_data(cnpj)["DT_REFER"].astype(str).unique())
                datas_all = dts if datas_all is None else datas_all & dts
            datas_disp = sorted(datas_all or [], reverse=True)
            if not datas_disp:
                st.warning("Sem datas em comum."); st.stop()
            data_ref = st.selectbox("Período:", datas_disp, key="cmp_data_emp")

            cnpj_unico = nome_unico = setor_sel = None

        # ── MODO 2 ──────────────────────────────────────────────────────────
        elif modo == "🏭 Empresa vs Setor":
            setor_filtro = st.selectbox("Filtrar empresa por setor:",
                                        ["(Todos)"] + setores_disp,
                                        key="cmp_setor_filtro_2")
            df_ef = (df_empresas[df_empresas.get("SETOR_ATIV", pd.Series(dtype=str))
                                 .fillna("").str.contains(setor_filtro, case=False)]
                     if setor_filtro != "(Todos)" and "SETOR_ATIV" in df_empresas.columns
                     else df_empresas)

            label_u = st.selectbox("Empresa:", df_ef["LABEL"].tolist(), key="cmp_emp_setor")
            cnpj_unico = mapa_emp[label_u]
            nome_unico = label_u.split(" (")[0]

            df_ed = get_indicadores_data(cnpj_unico)
            setor_auto = (df_ed["SETOR"].dropna().iloc[0]
                          if not df_ed.empty and "SETOR" in df_ed.columns
                             and not df_ed["SETOR"].dropna().empty else None)
            idx_def = setores_disp.index(setor_auto) if setor_auto in setores_disp else 0
            setor_sel = st.selectbox("Setor benchmark:", setores_disp,
                                     index=idx_def, key="cmp_setor_bench")
            datas_disp = sorted(df_ed["DT_REFER"].astype(str).unique(), reverse=True)
            data_ref = st.selectbox("Período:", datas_disp, key="cmp_data_setor")
            empresas_selecionadas = {}

        # ── MODO 3 ──────────────────────────────────────────────────────────
        else:
            setor_filtro = st.selectbox("Filtrar empresa por setor:",
                                        ["(Todos)"] + setores_disp,
                                        key="cmp_setor_filtro_3")
            df_ef = (df_empresas[df_empresas.get("SETOR_ATIV", pd.Series(dtype=str))
                                 .fillna("").str.contains(setor_filtro, case=False)]
                     if setor_filtro != "(Todos)" and "SETOR_ATIV" in df_empresas.columns
                     else df_empresas)

            label_u = st.selectbox("Empresa:", df_ef["LABEL"].tolist(), key="cmp_emp_global")
            cnpj_unico = mapa_emp[label_u]
            nome_unico = label_u.split(" (")[0]
            df_ed = get_indicadores_data(cnpj_unico)
            datas_disp = sorted(df_ed["DT_REFER"].astype(str).unique(), reverse=True)
            data_ref = st.selectbox("Período:", datas_disp, key="cmp_data_global")
            setor_sel           = None
            empresas_selecionadas = {}

    # ── CORPO ────────────────────────────────────────────────────────────────
    st.title("Comparativo de Empresas e Setores")
    st.markdown("---")

    if modo == "🏢 Empresa vs Empresa":
        render_empresa_vs_empresa(empresas_selecionadas, data_ref)

    elif modo == "🏭 Empresa vs Setor":
        render_empresa_vs_setor(cnpj_unico, nome_unico, setor_sel, data_ref)

    else:
        render_empresa_vs_todos_setores(cnpj_unico, nome_unico, data_ref)
