import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from database import get_dates_bp, get_bp_data_filtered
from chart_theme import (
    BG_TRANSPARENT, GRID_COLOR, ZERO_LINE_COLOR,
    FONT_COLOR, FONT_COLOR_TITLE, PALETA, FONT_FAMILY, LEGEND_BG,
    plot_chart,
)
from ai_analyst import (
    render_ai_panel,
    build_context_bp,
    _prompt_bp,
)
from glossary import chart_tooltip

import numpy as np

def formatar_moeda_br(valor):
    """
    Converte float para string no padrão brasileiro: 1.000,00
    """
    if pd.isna(valor):
        return "-"
    texto = f"{valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")

def style_validation_row(val):
    """
    Pinta de vermelho se houver diferença contábil significativa, verde se zerado.
    """
    if isinstance(val, (int, float)):
        if abs(val) > 0.01:
            return 'background-color: #ffcccc; color: #cc0000; font-weight: bold'
        return 'background-color: #e6fffa; color: #006600; font-weight: bold'
    return ''


def _render_sunburst_bp(df_ativo, df_passivo, cols_dates):
    """Sunburst interativo da estrutura patrimonial no último período."""
    st.subheader("Estrutura Patrimonial", help=chart_tooltip("sunburst_bp"))
    dt_ref = cols_dates[-1]

    ids, labels, parents, values, colors = [], [], [], [], []
    ids.append("root"); labels.append("Balanço"); parents.append(""); values.append(0)
    colors.append("rgba(0,0,0,0)")

    def add_group(df, grupo_id, grupo_label, grupo_cor):
        rows_raiz = df[df["CD_CONTA"].str.match(r"^\d$")]
        total = float(rows_raiz[dt_ref].sum()) if not rows_raiz.empty else 0
        ids.append(grupo_id); labels.append(grupo_label)
        parents.append("root"); values.append(abs(total)); colors.append(grupo_cor)
        rows_sub = df[df["CD_CONTA"].str.match(r"^\d\.\d+$")]
        for _, row in rows_sub.iterrows():
            v = abs(float(row[dt_ref])) if row[dt_ref] != 0 else 0
            if v < 0.001:
                continue
            sid = f"{grupo_id}_{row['CD_CONTA']}"
            ids.append(sid); labels.append(row["DS_CONTA"][:28])
            parents.append(grupo_id); values.append(v); colors.append(grupo_cor)

    add_group(df_ativo,  "ativo",   "Ativo",        PALETA[2])
    add_group(df_passivo,"passivo", "Passivo + PL",  PALETA[5])

    if len(ids) < 4:
        st.info("Dados insuficientes para o Sunburst.")
        return

    fig = go.Figure(go.Sunburst(
        ids=ids, labels=labels, parents=parents, values=values,
        marker=dict(colors=colors, line=dict(color="rgba(19,41,61,0.06)", width=1)),
        branchvalues="remainder",
        hovertemplate="<b>%{label}</b><br>%{value:,.2f}<br>%{percentRoot:.1%} do total<extra></extra>",
        textfont=dict(family=FONT_FAMILY, size=11, color=FONT_COLOR_TITLE),
        insidetextorientation="radial",
        maxdepth=3,
    ))
    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT, plot_bgcolor=BG_TRANSPARENT,
        font=dict(family=FONT_FAMILY, color=FONT_COLOR),
        height=430, margin=dict(t=10, b=10, l=10, r=10),
    )
    plot_chart(fig)
    st.caption(f"📅 Período: **{dt_ref}** — clique nos segmentos para explorar.")


def _render_evolucao_categorias(df_ativo, cols_dates, scale_option):
    """Área empilhada mostrando como as categorias do ativo evoluíram."""
    st.subheader("Evolução da Composição do Ativo", help=chart_tooltip("evolucao_ativo_bp"))

    cats = {
        "Caixa / Equiv.":  ("1.01.01", PALETA[0]),
        "Recebíveis":       ("1.01.03", PALETA[4]),
        "Estoques":         ("1.01.04", PALETA[5]),
        "Outros Circ.":     ("1.01.06", PALETA[6]),
        "Imobilizado":      ("1.02.03", PALETA[1]),
        "Intangível":       ("1.02.04", PALETA[3]),
        "Outros N.Circ.":   ("1.02.06", PALETA[2]),
    }

    fig = go.Figure()
    for nome, (code, cor) in cats.items():
        rows = df_ativo[df_ativo["CD_CONTA"] == code]
        if rows.empty:
            continue
        vals = [float(rows[d].iloc[0]) if d in rows.columns else 0 for d in cols_dates]
        if sum(abs(v) for v in vals) < 0.001:
            continue
        r, g, b = int(cor[1:3], 16), int(cor[3:5], 16), int(cor[5:7], 16)
        fig.add_trace(go.Scatter(
            x=cols_dates, y=vals, name=nome, mode="lines",
            stackgroup="ativo",
            line=dict(color=cor, width=1.2),
            fillcolor=f"rgba({r},{g},{b},0.50)",
            hovertemplate=f"{nome}: %{{y:,.2f}}<extra></extra>",
        ))

    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT, plot_bgcolor=BG_TRANSPARENT,
        font=dict(family=FONT_FAMILY, color=FONT_COLOR), height=430,
        xaxis=dict(type="category", tickfont=dict(color=FONT_COLOR), gridcolor=GRID_COLOR),
        yaxis=dict(tickfont=dict(color=FONT_COLOR), gridcolor=GRID_COLOR,
                   title_text=f"Valor ({scale_option})", title_font=dict(color=FONT_COLOR)),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
                    bgcolor=LEGEND_BG, font=dict(color=FONT_COLOR, size=10)),
        margin=dict(t=20, b=40, l=60, r=20), hovermode="x unified",
        hoverlabel=dict(bgcolor="rgba(19,41,61,0.92)", font=dict(color="#E8F1F2")),
    )
    plot_chart(fig)


def _render_estrutura_capital(df_ativo, df_passivo, cols_dates, scale_option):
    """Barras divergentes: Ativo (positivo) × Passivo+PL (negativo)."""
    st.subheader("Estrutura de Capital — Ativo vs Passivo", help=chart_tooltip("estrutura_capital_bp"))

    cats_ativo = [
        ("1.01", "Ativo Circulante",       PALETA[0]),
        ("1.02", "Ativo Não Circulante",    PALETA[2]),
    ]
    cats_passivo = [
        ("2.01", "Passivo Circulante",      PALETA[5]),
        ("2.02", "Passivo Não Circulante",  PALETA[7]),
        ("2.03", "Patrimônio Líquido",      PALETA[1]),
    ]

    fig = go.Figure()
    for code, nome, cor in cats_ativo:
        row = df_ativo[df_ativo["CD_CONTA"] == code]
        if row.empty:
            continue
        vals = [float(row[d].iloc[0]) if d in row.columns else 0 for d in cols_dates]
        r, g, b = int(cor[1:3], 16), int(cor[3:5], 16), int(cor[5:7], 16)
        fig.add_trace(go.Bar(
            name=nome, x=cols_dates, y=vals,
            marker=dict(color=f"rgba({r},{g},{b},0.85)", line=dict(width=0)),
            hovertemplate=f"{nome}: %{{y:,.2f}}<extra></extra>",
        ))

    for code, nome, cor in cats_passivo:
        row = df_passivo[df_passivo["CD_CONTA"] == code]
        if row.empty:
            continue
        vals = [-float(row[d].iloc[0]) if d in row.columns else 0 for d in cols_dates]
        r, g, b = int(cor[1:3], 16), int(cor[3:5], 16), int(cor[5:7], 16)
        fig.add_trace(go.Bar(
            name=nome, x=cols_dates, y=vals,
            marker=dict(color=f"rgba({r},{g},{b},0.85)", line=dict(width=0)),
            customdata=[-v for v in vals],
            hovertemplate=f"{nome}: %{{customdata:,.2f}}<extra></extra>",
        ))

    fig.add_hline(y=0, line_color=ZERO_LINE_COLOR, line_width=1.5)
    fig.update_layout(
        barmode="relative",
        paper_bgcolor=BG_TRANSPARENT, plot_bgcolor=BG_TRANSPARENT,
        font=dict(family=FONT_FAMILY, color=FONT_COLOR), height=400,
        xaxis=dict(type="category", tickfont=dict(color=FONT_COLOR), gridcolor=GRID_COLOR),
        yaxis=dict(tickfont=dict(color=FONT_COLOR), gridcolor=GRID_COLOR,
                   title_text=f"Valor ({scale_option})", title_font=dict(color=FONT_COLOR),
                   zeroline=True, zerolinecolor=ZERO_LINE_COLOR),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
                    bgcolor=LEGEND_BG, font=dict(color=FONT_COLOR, size=10)),
        margin=dict(t=30, b=40, l=60, r=20), hovermode="x unified",
        hoverlabel=dict(bgcolor="rgba(19,41,61,0.92)", font=dict(color="#E8F1F2")),
        annotations=[dict(
            text="▲ Ativo &nbsp;&nbsp; ▼ Passivo + PL",
            xref="paper", yref="paper", x=0, y=1.05,
            showarrow=False, font=dict(color=FONT_COLOR, size=11),
        )],
    )
    plot_chart(fig)


def render_bp_page():
    
    selected_cnpj = st.session_state.get("global_cnpj")
    selected_label = st.session_state.get("global_label", "")
    if not selected_cnpj:
        st.warning("Selecione uma empresa na barra lateral.")
        return

    with st.sidebar:
        # B. Seleção de Datas
        df_dates = get_dates_bp(selected_cnpj)
        available_dates = df_dates['DT_REFER'].astype(str).tolist()
        
        if not available_dates:
            st.error("Sem dados para esta empresa.")
            return

        # Padrão: Seleciona as 5 últimas datas disponíveis se possível
        selected_dates = st.multiselect(
            "Selecione os Períodos:",
            options=available_dates,
            default=available_dates[:5] if len(available_dates) >= 5 else available_dates
        )
        
        if not selected_dates:
            st.warning("Selecione pelo menos uma data.")
            return

        st.markdown("---")

        # C. Parâmetros Visuais
        level_selected = st.slider("Nível de Detalhe:", 1, 5, 3)
        scale_option = st.radio(
            "Escala de Valores:",
            ["Unidade (R$)", "Milhares (Mil)", "Milhões (MM)", "Bilhões (Bi)"],
            index=1
        )
        
        # Mapa de Escalas
        escala_map = {
            "Unidade (R$)": 1,
            "Milhares (Mil)": 1000,
            "Milhões (MM)": 1000000,
            "Bilhões (Bi)": 1000000000
        }
        divisor = escala_map[scale_option]

    nome_empresa = selected_label.split(' (')[0]
    st.title(f"{nome_empresa}")
    st.caption(f"**CNPJ:** {selected_cnpj} | **Análise de Balanço Patrimonial**")

    with st.spinner(f"Processando dados de {nome_empresa}..."):
        df_raw = get_bp_data_filtered(selected_cnpj, selected_dates, level_selected)
        
        if df_raw.empty:
            st.info("Nenhum dado encontrado.")
            return

        # Aplica escala
        df_raw['VL_CONTA_TRATADO'] = df_raw['VL_CONTA_TRATADO'] / divisor
        
        # Pivot: Linhas=Contas, Colunas=Datas
        df_pivot = df_raw.pivot_table(
            values='VL_CONTA_TRATADO',
            index=['CD_CONTA', 'DS_CONTA'],
            columns='DT_REFER',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        # Converte colunas Timestamp -> string 'YYYY-MM-DD' (DT_REFER vem como DATE do PostgreSQL)
        df_pivot.columns = [
            c.strftime('%Y-%m-%d') if hasattr(c, 'strftime') else c
            for c in df_pivot.columns
        ]

        # Garante que as colunas de data sejam strings ordenadas
        cols_dates = sorted([c for c in df_pivot.columns if c not in ['CD_CONTA', 'DS_CONTA']])

        # Reorganiza colunas finais
        df_pivot = df_pivot[['CD_CONTA', 'DS_CONTA'] + cols_dates]

    df_ativo = df_pivot[df_pivot['CD_CONTA'].str.startswith('1')].copy()
    df_passivo = df_pivot[df_pivot['CD_CONTA'].str.startswith('2')].copy()

    # Helpers para totais
    get_total = lambda df, code: df[df['CD_CONTA'] == code][cols_dates].iloc[0] if not df[df['CD_CONTA'] == code].empty else pd.Series(0, index=cols_dates)

    total_ativo = get_total(df_ativo, '1')
    total_passivo = get_total(df_passivo, '2')
    diff_check = total_ativo - total_passivo

    var_pct = total_ativo.pct_change().fillna(0) # YoY

    # CAGR Total
    if len(total_ativo) >= 2:
        val_inicial = total_ativo.iloc[0]
        val_final = total_ativo.iloc[-1]
        anos = len(total_ativo) - 1
        if val_inicial > 0:
            cagr_val = (val_final / val_inicial) ** (1/anos) - 1
        else:
            cagr_val = 0
    else:
        cagr_val = 0

    # Cria linha de validação para a tabela final
    row_check = pd.DataFrame([diff_check.tolist()], columns=cols_dates)
    row_check.insert(0, 'DS_CONTA', 'Diferença (Ativo - Passivo)')

    
    col_config_dates = {col: st.column_config.TextColumn(col, width="small") for col in cols_dates}
    
    col_config_base = {
        "CD_CONTA": st.column_config.TextColumn("Conta", width="small"),
        "DS_CONTA": st.column_config.TextColumn("Descrição", width="medium"),
        **col_config_dates
    }

    def show_table(df_input, header_emoji, header_title):
        st.subheader(f"{header_emoji} {header_title} ({scale_option})")
        df_view = df_input.copy()
        for c in cols_dates:
            df_view[c] = df_view[c].apply(formatar_moeda_br)
            
        # 35px por linha de dados + 38px do cabeçalho + 3px de borda/folga
        # Limitamos a 600px para não ficar infinito se tiver 1000 linhas (cria scroll nesse caso)
        altura_dinamica = (len(df_view) + 1) * 35 + 3
        
        # Opcional: Trava em um máximo se quiser (ex: max(altura, 600))
        # Se quiser mostrar TUDO sem scroll nunca, remova a função min()
        
        st.dataframe(
            df_view,
            hide_index=True,
            use_container_width=True,
            column_config=col_config_base,
            height=altura_dinamica # <--- AQUI A MÁGICA
        )

    show_table(df_ativo, "", "Ativo")
    st.markdown("###")
    show_table(df_passivo, "", "Passivo e Patrimônio Líquido")
    st.markdown("###")

    st.subheader("Validação e Crescimento", help=chart_tooltip("validacao_crescimento_bp"))
    
    eixo_x_str = [str(d) for d in cols_dates] 

    # 1. Finanças: Pega o maior valor e adiciona 25% de folga para caber os rótulos
    max_valor_fin = max(total_ativo.max(), total_passivo.max())
    range_fin = [-max_valor_fin * 1.25, max_valor_fin * 1.25]

    # 2. Porcentagem: Pega a maior variação e adiciona 35% de folga
    max_valor_pct = var_pct.abs().max()
    if pd.isna(max_valor_pct) or max_valor_pct == 0: max_valor_pct = 0.10
    range_pct = [-max_valor_pct * 1.35, max_valor_pct * 1.35]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.20, # <--- AUMENTADO (De 0.15 para 0.20) para separar bem os gráficos
        row_heights=[0.70, 0.30], # Leve ajuste para dar mais peso ao gráfico de barras
        subplot_titles=(f"Equilíbrio Patrimonial ({scale_option})", "Variação do Ativo (YoY)")
    )

    # Estilo dos Rótulos
    fonte_rotulos = dict(color=FONT_COLOR, size=13, family=FONT_FAMILY)

    fig.add_trace(go.Bar(
        x=eixo_x_str,
        y=total_ativo.values,
        name='Ativo Total',
        marker_color=PALETA[2],
        text=[formatar_moeda_br(v) for v in total_ativo.values], 
        textposition='outside',
        textfont=fonte_rotulos,
        hovertemplate='Ativo: %{y:,.2f}<extra></extra>'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=eixo_x_str,
        y=total_passivo.values * -1, 
        name='Passivo + PL',
        marker_color=PALETA[7],
        text=[formatar_moeda_br(v) for v in total_passivo.values],
        textposition='outside',
        textfont=fonte_rotulos,
        hovertemplate='Passivo: %{text}<extra></extra>'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=eixo_x_str,
        y=var_pct.values,
        name='Crescimento (%)',
        mode='lines+markers+text',
        line=dict(color=PALETA[1], width=3),
        marker=dict(size=8, symbol='circle', color=PALETA[1],
                    line=dict(width=1.5, color='rgba(255,255,255,0.3)')),
        text=[f"{v:.1%}" if i > 0 else "" for i, v in enumerate(var_pct.values)], 
        textposition="bottom center",
        textfont=dict(color=PALETA[1], size=12, weight='bold'),
        hovertemplate='Crescimento: %{y:.2%}<extra></extra>'
    ), row=2, col=1)

    fig.update_layout(
        title=dict(
            text=f"Análise de Evolução | CAGR de Ativo Total do Período Selecionado: {cagr_val:.1%}",
            font=dict(size=16, color=FONT_COLOR_TITLE, family=FONT_FAMILY),
            x=0.01,
            y=0.98,
            xanchor='left',
            yanchor='top'
        ),
        barmode='relative',
        plot_bgcolor=BG_TRANSPARENT,
        paper_bgcolor=BG_TRANSPARENT,
        height=800,
        showlegend=True,
        font=dict(family=FONT_FAMILY, color=FONT_COLOR),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.95,
            xanchor="center",
            x=0.5,
            bgcolor=LEGEND_BG,
            bordercolor='rgba(255,255,255,0.10)',
            borderwidth=1,
            font=dict(color=FONT_COLOR, size=12)
        ),
        margin=dict(t=160, b=50, l=50, r=50),
        hoverlabel=dict(
            bgcolor='rgba(15,15,30,0.85)',
            bordercolor='rgba(255,255,255,0.15)',
            font=dict(color='#F1F5F9', family=FONT_FAMILY, size=12),
        ),
    )

    
    # Eixo Y da Linha 1 (Barras)
    fig.update_yaxes(
        title_text="Valor Monetário",
        showgrid=True, gridcolor=GRID_COLOR,
        zeroline=True, zerolinecolor=ZERO_LINE_COLOR,
        tickfont=dict(color=FONT_COLOR),
        title_font=dict(color=FONT_COLOR),
        range=range_fin,
        row=1, col=1
    )
    fig.add_shape(type='line', y0=0, y1=0, x0=-0.5, x1=len(cols_dates)-0.5, 
                  line=dict(color=ZERO_LINE_COLOR, width=1.5), row=1, col=1)

    # Eixo Y da Linha 2 (Crescimento)
    fig.update_yaxes(
        title_text="Crescimento (%)",
        tickformat='.0%',
        showgrid=True, gridcolor=GRID_COLOR,
        zeroline=True, zerolinecolor=ZERO_LINE_COLOR,
        tickfont=dict(color=FONT_COLOR),
        title_font=dict(color=FONT_COLOR),
        range=range_pct,
        row=2, col=1
    )
    fig.add_shape(type='line', y0=0, y1=0, x0=-0.5, x1=len(cols_dates)-0.5, 
                  line=dict(color=ZERO_LINE_COLOR, width=1, dash='dot'), row=2, col=1)
    
    fig.update_xaxes(type='category', row=1, col=1)
    fig.update_xaxes(type='category', row=2, col=1)
    
    # Ajuste manual da posição dos Títulos dos Subplots (Annotations)
    # Isso garante que eles fiquem no lugar certo
    fig.update_annotations(
        x=0,             # Força a posição para o início do eixo X (0 = Esquerda)
        xanchor='left',  # Ancora o texto pela esquerda (ele cresce para a direita)
        font_size=16,    # Tamanho da fonte
        yshift=30        # Sobe o título 30 pixels para desgrudar do gráfico (ajuste conforme gosto)
    )

    plot_chart(fig)

    with st.expander("ℹ️ Entenda as Métricas de Crescimento"):
        st.markdown(f"""
        **1. CAGR ({cagr_val:.1%}):** *Compound Annual Growth Rate* (Taxa de Crescimento Anual Composta). 
        Representa a taxa de retorno necessária para um investimento crescer do seu saldo inicial para o saldo final, assumindo que os lucros foram reinvestidos ao final de cada ano da vida do investimento.
        
        $ \\displaystyle CAGR = \\left( \\frac{{Valor_{{Final}}}}{{Valor_{{Inicial}}}} \\right)^{{\\frac{{1}}{{n}}}} - 1 $
        
        Onde:
        * **$Valor_{{Final}}$**: Valor do Ativo Total no último período selecionado.
        * **$Valor_{{Inicial}}$**: Valor do Ativo Total no primeiro período selecionado.
        * **$n$**: Número de anos (ou períodos) decorridos.

        ---
        **2. Crescimento do Ativo Total (Linha Azul - YoY):** *Year over Year*. É a variação percentual simples do Ativo em relação ao período imediatamente anterior (mostrada no gráfico inferior).
        """)

    st.dataframe(
        row_check.style
            .map(style_validation_row, subset=cols_dates)
            .format(formatar_moeda_br, subset=cols_dates),
        hide_index=True,
        use_container_width=True,
        column_config={
            "DS_CONTA": st.column_config.TextColumn("Status da Validação", width="large"),
            **col_config_dates
        }
    )

    if diff_check.abs().max() > 0.1:
        st.error(f"⚠️ Existem divergências contábeis significativas na escala {scale_option}!")
    else:
        st.success("Balanço validado: Ativo = Passivo + PL em todos os períodos.")

    st.markdown("---")

    st.subheader("Análise Visual Avançada")
    col_g1, col_g2 = st.columns([1, 1])
    with col_g1:
        _render_sunburst_bp(df_ativo, df_passivo, cols_dates)
    with col_g2:
        _render_evolucao_categorias(df_ativo, cols_dates, scale_option)

    st.markdown("###")
    _render_estrutura_capital(df_ativo, df_passivo, cols_dates, scale_option)

    st.markdown("---")
    ctx_bp = build_context_bp(df_pivot, cols_dates, nome_empresa, scale_option)
    render_ai_panel(
        contexto=ctx_bp,
        prompt_fn=lambda c: _prompt_bp(c, nome_empresa),
        titulo="Análise da IA — Balanço Patrimonial",
        panel_key=f"bp_{selected_cnpj}",
    )
