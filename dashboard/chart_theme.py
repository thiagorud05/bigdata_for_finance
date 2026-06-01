import plotly.graph_objects as go
import plotly.io as pio

PALETA = [
    "#A855F7",  # roxo
    "#38BDF8",  # azul céu
    "#34D399",  # verde esmeralda
    "#FB923C",  # laranja
    "#F472B6",  # rosa
    "#FACC15",  # âmbar
    "#60A5FA",  # azul claro
    "#F87171",  # vermelho suave
]

CORES = {
    "roxo":       "#A855F7",
    "roxo_claro": "#C084FC",
    "azul":       "#38BDF8",
    "verde":      "#34D399",
    "laranja":    "#FB923C",
    "rosa":       "#F472B6",
    "dourado":    "#FACC15",
    "vermelho":   "#F87171",
    "cinza":      "#94A3B8",
    "branco":     "#F1F5F9",
}

BG_TRANSPARENT   = "rgba(0,0,0,0)"
GRID_COLOR       = "rgba(255,255,255,0.06)"
ZERO_LINE_COLOR  = "rgba(255,255,255,0.20)"
AXIS_LINE_COLOR  = "rgba(255,255,255,0.12)"
FONT_COLOR       = "#CBD5E1"
FONT_COLOR_TITLE = "#F1F5F9"
FONT_FAMILY      = "Inter, system-ui, sans-serif"
LEGEND_BG        = "rgba(15,15,30,0.55)"


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
            bordercolor="rgba(255,255,255,0.10)",
            borderwidth=1,
            font=dict(color=FONT_COLOR, size=11),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(15,15,30,0.85)",
            bordercolor="rgba(255,255,255,0.15)",
            font=dict(color="#F1F5F9", family=FONT_FAMILY, size=12),
        ),
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
    # secondary_y só pode ser passado em figuras criadas com make_subplots
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
        marker=dict(size=7, color=color, line=dict(width=1.5, color="rgba(255,255,255,0.3)")),
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
                        fill_opacity: float = 0.12) -> go.Scatterpolar:
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
            bordercolor="rgba(255,255,255,0.10)",
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
        ),
    )
    return fig
