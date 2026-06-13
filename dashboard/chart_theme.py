import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

# Configuração padrão para todos os gráficos Plotly:
# - dragmode pan: arrastar move o gráfico em vez de dar zoom
# - scrollZoom off: scroll do mouse/touch não dá zoom
# - doubleClick reset: duplo clique volta à visão original
PLOTLY_CONFIG = {
    "scrollZoom": False,
    "doubleClick": "reset",
    "displayModeBar": "hover",
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "toImageButtonOptions": {"format": "png", "scale": 2},
}

# Brand palette — pastel blue-family light theme
PALETA = [
    "#90CAF9",  # Pastel Blue        — série principal
    "#CE93D8",  # Pastel Lavender    — série secundária
    "#80DEEA",  # Pastel Cyan        — série terciária / positivo
    "#9FA8DA",  # Pastel Periwinkle  — acento índigo
    "#A5D6A7",  # Pastel Sage Green  — contraste complementar
    "#80CBC4",  # Pastel Teal        — acento azul-verde
    "#B39DDB",  # Pastel Purple      — neutro violeta
    "#EF9A9A",  # Pastel Red         — negativo / alerta
]

CORES = {
    "azul":        "#90CAF9",
    "azul_escuro": "#5BA3C9",
    "azul_medio":  "#80DEEA",
    "prussian":    "#13293D",
    "teal":        "#80CBC4",
    "coral":       "#EF9A9A",
    "steel":       "#9FA8DA",
    "laranja":     "#B39DDB",
    "verde":       "#A5D6A7",
    "vermelho":    "#EF9A9A",
    "roxo":        "#CE93D8",
    "dourado":     "#80DEEA",
    "cinza":       "#B0BEC5",
    "branco":      "#F5F5F5",
}

BG_TRANSPARENT  = "rgba(0,0,0,0)"
GRID_COLOR      = "rgba(19,41,61,0.07)"
ZERO_LINE_COLOR = "rgba(0,100,148,0.22)"
AXIS_LINE_COLOR = "rgba(19,41,61,0.14)"
FONT_COLOR      = "#13293D"
FONT_COLOR_TITLE = "#006494"
FONT_FAMILY     = "Inter, system-ui, sans-serif"
LEGEND_BG       = "rgba(232,241,242,0.92)"

HOVER_BG   = "rgba(19,41,61,0.92)"
HOVER_FONT = "#E8F1F2"


def _base_layout(height: int = 380, title: str = None) -> dict:
    layout = dict(
        plot_bgcolor=BG_TRANSPARENT,
        paper_bgcolor=BG_TRANSPARENT,
        font=dict(family=FONT_FAMILY, color=FONT_COLOR, size=12),
        height=height,
        margin=dict(t=48 if title else 28, b=44, l=56, r=32),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor=LEGEND_BG,
            bordercolor=AXIS_LINE_COLOR,
            borderwidth=1,
            font=dict(color=FONT_COLOR, size=11),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=HOVER_BG,
            bordercolor=AXIS_LINE_COLOR,
            font=dict(color=HOVER_FONT, family=FONT_FAMILY, size=12),
        ),
        dragmode="pan",
    )
    if title:
        layout["title"] = dict(
            text=title,
            font=dict(color=FONT_COLOR_TITLE, size=15, family=FONT_FAMILY),
            x=0.0,
            xanchor="left",
        )
    return layout


def _axis_style(title_text: str = None, tick_suffix: str = "",
                tick_format: str = None, show_grid: bool = True,
                is_category: bool = False) -> dict:
    style = dict(
        showgrid=show_grid,
        gridcolor=GRID_COLOR,
        gridwidth=1,
        zeroline=True,
        zerolinecolor=ZERO_LINE_COLOR,
        zerolinewidth=1,
        linecolor=AXIS_LINE_COLOR,
        tickcolor=AXIS_LINE_COLOR,
        tickfont=dict(color=FONT_COLOR, size=11),
        title_font=dict(color=FONT_COLOR, size=12),
    )
    if title_text:
        style["title_text"] = title_text
    if tick_suffix:
        style["ticksuffix"] = tick_suffix
    if tick_format:
        style["tickformat"] = tick_format
    if is_category:
        style["type"] = "category"
    return style


def apply_theme(
    fig: go.Figure,
    height: int = 380,
    title: str = None,
    x_is_category: bool = True,
    y_title: str = None,
    y_suffix: str = "",
    y_format: str = None,
    y2_title: str = None,
    hovermode: str = "x unified",
) -> go.Figure:
    layout = _base_layout(height=height, title=title)
    layout["hovermode"] = hovermode
    fig.update_layout(**layout)

    fig.update_xaxes(**_axis_style(is_category=x_is_category))

    y_kw = _axis_style(title_text=y_title, tick_suffix=y_suffix, tick_format=y_format)
    if y2_title:
        fig.update_yaxes(**y_kw, secondary_y=False)
        fig.update_yaxes(**_axis_style(title_text=y2_title, show_grid=False), secondary_y=True)
    else:
        fig.update_yaxes(**y_kw)

    return fig


def bar_trace(x, y, name: str, color: str, text=None,
              opacity: float = 0.90, **kwargs) -> go.Bar:
    return go.Bar(
        x=x, y=y, name=name,
        marker=dict(color=color, opacity=opacity, line=dict(width=0)),
        text=text,
        textposition="outside" if text is not None else "none",
        textfont=dict(color=FONT_COLOR, size=10),
        hovertemplate=f"<b>{name}</b>: %{{y}}<extra></extra>",
        **kwargs,
    )


def line_trace(x, y, name: str, color: str, width: float = 2.5,
               dash: str = None, show_text: bool = False,
               text=None, text_pos: str = "top center", **kwargs) -> go.Scatter:
    line_style = dict(color=color, width=width)
    if dash:
        line_style["dash"] = dash

    trace_kwargs = dict(
        x=x, y=y, name=name,
        mode="lines+markers" + ("+text" if show_text and text is not None else ""),
        line=line_style,
        marker=dict(size=7, color=color, line=dict(width=1.5, color="rgba(255,255,255,0.5)")),
        hovertemplate=f"<b>{name}</b>: %{{y}}<extra></extra>",
        **kwargs,
    )
    if show_text and text is not None:
        trace_kwargs["text"] = text
        trace_kwargs["textposition"] = text_pos
        trace_kwargs["textfont"] = dict(color=color, size=10)

    return go.Scatter(**trace_kwargs)


def area_trace(x, y, name: str, color: str, fill_opacity: float = 0.15,
               **kwargs) -> go.Scatter:
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    return go.Scatter(
        x=x, y=y, name=name,
        mode="lines",
        line=dict(color=color, width=2.5),
        fill="tozeroy",
        fillcolor=f"rgba({r},{g},{b},{fill_opacity})",
        hovertemplate=f"<b>{name}</b>: %{{y}}<extra></extra>",
        **kwargs,
    )


def scatter_polar_trace(r, theta, name: str, color: str,
                        fill_opacity: float = 0.15) -> go.Scatterpolar:
    rv = int(color[1:3], 16)
    gv = int(color[3:5], 16)
    bv = int(color[5:7], 16)
    return go.Scatterpolar(
        r=r, theta=theta,
        fill="toself",
        name=name,
        line=dict(color=color, width=2.2),
        fillcolor=f"rgba({rv},{gv},{bv},{fill_opacity})",
        marker=dict(size=5, color=color),
    )


def apply_polar_theme(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        polar=dict(
            bgcolor=BG_TRANSPARENT,
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickvals=[0.25, 0.5, 0.75, 1.0],
                ticktext=["25%", "50%", "75%", "100%"],
                tickfont=dict(size=9, color=FONT_COLOR),
                gridcolor=GRID_COLOR,
                linecolor=AXIS_LINE_COLOR,
                tickcolor=AXIS_LINE_COLOR,
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color=FONT_COLOR_TITLE),
                gridcolor=GRID_COLOR,
                linecolor=AXIS_LINE_COLOR,
            ),
        ),
        paper_bgcolor=BG_TRANSPARENT,
        plot_bgcolor=BG_TRANSPARENT,
        font=dict(family=FONT_FAMILY, color=FONT_COLOR),
        showlegend=True,
        height=height,
        margin=dict(t=30, b=60, l=60, r=60),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=-0.22,
            xanchor="center", x=0.5,
            bgcolor=LEGEND_BG,
            bordercolor=AXIS_LINE_COLOR,
            borderwidth=1,
            font=dict(color=FONT_COLOR, size=11),
        ),
    )
    return fig


def apply_heatmap_theme(fig: go.Figure, height: int = 500) -> go.Figure:
    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT,
        plot_bgcolor=BG_TRANSPARENT,
        font=dict(family=FONT_FAMILY, color=FONT_COLOR),
        height=height,
        margin=dict(t=20, b=80, l=200, r=60),
        xaxis=dict(
            tickangle=-30,
            tickfont=dict(color=FONT_COLOR, size=10),
            linecolor=AXIS_LINE_COLOR,
        ),
        yaxis=dict(
            tickfont=dict(color=FONT_COLOR, size=10),
            linecolor=AXIS_LINE_COLOR,
            autorange="reversed",   # empresa (★) fica na primeira linha do topo
        ),
    )
    return fig


def plot_chart(fig: go.Figure, **kwargs) -> None:
    """Wrapper centralizado para st.plotly_chart com config padrão (pan, sem zoom acidental)."""
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, **kwargs)

