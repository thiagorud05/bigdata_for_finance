import os
import streamlit as st
import pandas as pd
import numpy as np

# Inicialização lazy — o cliente só é criado quando o botão é clicado,
# evitando erro de import ou de API key ausente na inicialização do app.
def _get_groq_client():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return None, "GROQ_API_KEY não configurada no arquivo .env."

    try:
        from groq import Groq
        return Groq(api_key=api_key), None
    except ImportError:
        return None, "Pacote `groq` não instalado. Execute: pip install groq"
    except Exception as e:
        return None, f"Erro ao inicializar cliente Groq: {e}"


def _call_groq(system_prompt: str, user_prompt: str,
               model: str = "llama-3.3-70b-versatile",
               max_tokens: int = 1200) -> tuple[str | None, str | None]:
    client, err = _get_groq_client()
    if client is None:
        return None, err

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        texto = response.choices[0].message.content
        return texto, None
    except Exception as e:
        return None, f"Erro na chamada à API Groq: {e}"


_SYSTEM_BASE = """
Você é um analista financeiro sênior especializado em empresas de capital aberto
brasileiras listadas na CVM (Comissão de Valores Mobiliários).

Suas análises devem:
- Ser objetivas, diretas e baseadas estritamente nos dados fornecidos.
- Destacar pontos positivos e negativos de forma equilibrada.
- Usar linguagem acessível mas profissional, em português do Brasil.
- Evitar especulações que vão além dos dados apresentados.
- Estruturar a resposta com seções curtas e bullet points quando útil.
- Não inventar dados ou citar valores que não foram fornecidos.
""".strip()

def _fmt(val, tipo="pct", decimais=1):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/D"
    if tipo == "pct":
        return f"{val * 100:.{decimais}f}%"
    if tipo == "num":
        return f"{val:.{decimais}f}"
    if tipo == "dias":
        return f"{val:.0f} dias"
    if tipo == "mm":
        return f"R$ {val / 1e6:,.1f} MM"
    return str(val)


def build_context_indicadores(df: pd.DataFrame, empresa: str) -> str:
    """
    Constrói o contexto textual para análise de uma empresa a partir
    do DataFrame de indicadores financeiros (mart_indicadores_financeiros).
    """
    if df.empty:
        return "Sem dados disponíveis."

    df_s = df.sort_values("DT_REFER")
    ultima = df_s.iloc[-1]
    periodos = df_s["DT_REFER"].astype(str).tolist()

    def g(col):
        v = ultima.get(col, None)
        return None if v is None or (isinstance(v, float) and np.isnan(v)) else float(v)

    def serie(col):
        if col not in df_s.columns:
            return []
        return [(str(r["DT_REFER"]), r[col]) for _, r in df_s.iterrows()
                if r[col] is not None and not (isinstance(r[col], float) and np.isnan(r[col]))]

    linhas = [
        f"EMPRESA: {empresa}",
        f"PERÍODOS ANALISADOS: {', '.join(periodos)}",
        f"ÚLTIMO PERÍODO: {str(ultima.get('DT_REFER', 'N/D'))}",
        "",
        "=== RENTABILIDADE (último período) ===",
        f"  Margem Líquida:  {_fmt(g('MARGEM_LIQUIDA'))}",
        f"  Margem Bruta:    {_fmt(g('MARGEM_BRUTA'))}",
        f"  Margem EBIT:     {_fmt(g('MARGEM_EBIT'))}",
        f"  ROE:             {_fmt(g('ROE'))}",
        f"  ROA:             {_fmt(g('ROA'))}",
        "",
        "=== LIQUIDEZ (último período) ===",
        f"  Liq. Corrente:   {_fmt(g('LIQUIDEZ_CORRENTE'), 'num')}",
        f"  Liq. Seca:       {_fmt(g('LIQUIDEZ_SECA'), 'num')}",
        f"  Liq. Imediata:   {_fmt(g('LIQUIDEZ_IMEDIATA'), 'num')}",
        f"  Endividamento:   {_fmt(g('ENDIVIDAMENTO_GERAL'))}",
        f"  Grau Endivid.:   {_fmt(g('GRAU_ENDIVIDAMENTO'), 'num')}",
        "",
        "=== DEMONSTRAÇÃO DE RESULTADOS (último período, R$ MM) ===",
        f"  Receita Líquida: {_fmt(g('V16'), 'mm')}",
        f"  Lucro Bruto:     {_fmt(g('V18'), 'mm')}",
        f"  EBIT:            {_fmt(g('V20'), 'mm')}",
        f"  Lucro Líquido:   {_fmt(g('V23'), 'mm')}",
        "",
        "=== CICLOS OPERACIONAIS (último período) ===",
        f"  PMRV:            {_fmt(g('PMRV'), 'dias')}",
        f"  PME:             {_fmt(g('PME'), 'dias')}",
        f"  PMPF:            {_fmt(g('PMPF'), 'dias')}",
        f"  Ciclo Operac.:   {_fmt(g('CICLO_OPERACIONAL'), 'dias')}",
        f"  Ciclo Financ.:   {_fmt(g('CICLO_FINANCEIRO'), 'dias')}",
        "",
        "=== EVOLUÇÃO DA MARGEM LÍQUIDA (série histórica) ===",
    ]

    for dt, v in serie("MARGEM_LIQUIDA"):
        linhas.append(f"  {dt}: {_fmt(v)}")

    setor = ultima.get("SETOR", None)
    if setor and str(setor) != "nan":
        linhas.append(f"\nSETOR: {setor}")

    return "\n".join(linhas)


def build_context_comparativo_empresas(dfs: dict, data_ref: str) -> str:
    """
    Constrói contexto para comparativo entre múltiplas empresas.
    dfs: {nome_empresa: Series/row}
    """
    indicadores = {
        "MARGEM_LIQUIDA":    ("Margem Líquida",  "pct"),
        "MARGEM_BRUTA":      ("Margem Bruta",    "pct"),
        "ROE":               ("ROE",             "pct"),
        "ROA":               ("ROA",             "pct"),
        "LIQUIDEZ_CORRENTE": ("Liq. Corrente",   "num"),
        "ENDIVIDAMENTO_GERAL":("Endividamento",  "pct"),
        "CICLO_FINANCEIRO":  ("Ciclo Financ.",   "dias"),
    }

    linhas = [
        f"COMPARATIVO DE EMPRESAS — PERÍODO: {data_ref}",
        "",
    ]

    for nome, row in dfs.items():
        linhas.append(f"--- {nome} ---")
        for col, (label, tipo) in indicadores.items():
            v = row.get(col, None)
            vf = None if v is None or (isinstance(v, float) and np.isnan(v)) else float(v)
            linhas.append(f"  {label}: {_fmt(vf, tipo)}")
        linhas.append("")

    return "\n".join(linhas)


def build_context_vs_setor(emp_row, bench_row, nome_empresa: str,
                           setor: str, data_ref: str) -> str:
    """Contexto para comparativo empresa vs mediana do setor."""
    indicadores = {
        "MARGEM_LIQUIDA":    ("Margem Líquida",  "pct"),
        "MARGEM_BRUTA":      ("Margem Bruta",    "pct"),
        "ROE":               ("ROE",             "pct"),
        "ROA":               ("ROA",             "pct"),
        "LIQUIDEZ_CORRENTE": ("Liq. Corrente",   "num"),
        "ENDIVIDAMENTO_GERAL":("Endividamento",  "pct"),
        "PMRV":              ("PMRV",            "dias"),
        "CICLO_FINANCEIRO":  ("Ciclo Financ.",   "dias"),
    }

    linhas = [
        f"EMPRESA vs SETOR — PERÍODO: {data_ref}",
        f"Empresa: {nome_empresa} | Setor benchmark: {setor}",
        "",
        f"{'INDICADOR':<22} {'EMPRESA':>12} {'MEDIANA SETOR':>15} {'DIFERENÇA':>12}",
        "-" * 65,
    ]

    for col, (label, tipo) in indicadores.items():
        ve_raw = emp_row.get(col, None)
        vb_raw = bench_row.get(col, None)
        ve = None if ve_raw is None or (isinstance(ve_raw, float) and np.isnan(ve_raw)) else float(ve_raw)
        vb = None if vb_raw is None or (isinstance(vb_raw, float) and np.isnan(vb_raw)) else float(vb_raw)

        str_e = _fmt(ve, tipo)
        str_b = _fmt(vb, tipo)

        if ve is not None and vb is not None and vb != 0:
            diff_pct = (ve - vb) / abs(vb) * 100
            str_d = f"{diff_pct:+.1f}%"
        else:
            str_d = "N/D"

        linhas.append(f"  {label:<20} {str_e:>12} {str_b:>15} {str_d:>12}")

    return "\n".join(linhas)


def _prompt_indicadores(contexto: str, empresa: str) -> str:
    return f"""
Analise os indicadores financeiros abaixo da empresa {empresa}.

{contexto}

Por favor, forneça:
1. **Saúde Financeira Geral** — avaliação rápida do estado atual da empresa.
2. **Pontos Fortes** — o que se destaca positivamente nos dados.
3. **Pontos de Atenção** — riscos ou fraquezas identificados.
4. **Tendência Histórica** — o que a evolução da Margem Líquida sugere.
5. **Conclusão** — uma frase objetiva resumindo o posicionamento financeiro.

Seja conciso. Use bullet points nas seções 2, 3 e 4.
""".strip()


def _prompt_comparativo(contexto: str, modo: str) -> str:
    return f"""
Analise o comparativo financeiro abaixo ({modo}).

{contexto}

Por favor, forneça:
1. **Destaques** — qual empresa/setor se sobressai e por quê.
2. **Pontos de Divergência** — onde há maiores diferenças e o que isso indica.
3. **Análise de Risco** — qual apresenta maior/menor perfil de risco.
4. **Recomendação de Foco** — onde um analista deveria aprofundar a investigação.

Seja conciso e direto. Use bullet points.
""".strip()


def build_context_bp(df_pivot: pd.DataFrame, cols_dates: list,
                     empresa: str, scale_option: str = "Milhões (MM)") -> str:
    """
    Constrói contexto textual para análise do Balanço Patrimonial.
    df_pivot: pivot já aplicado (CD_CONTA, DS_CONTA, <datas>).
    """
    if df_pivot.empty or not cols_dates:
        return "Sem dados disponíveis."

    def get_row(code):
        r = df_pivot[df_pivot["CD_CONTA"] == code]
        return r[cols_dates].iloc[0] if not r.empty else pd.Series(0.0, index=cols_dates)

    ativo    = get_row("1")
    passivo  = get_row("2")
    ativo_c  = get_row("1.01")
    ativo_nc = get_row("1.02")
    pass_c   = get_row("2.01")
    pass_nc  = get_row("2.02")
    pl       = get_row("2.03")

    ultimo = cols_dates[-1]
    anterior = cols_dates[-2] if len(cols_dates) >= 2 else None

    def v(serie): return float(serie[ultimo]) if ultimo in serie.index else None
    def yoy(serie):
        if anterior is None: return None
        a, b = float(serie[anterior]), float(serie[ultimo])
        return (b - a) / abs(a) * 100 if a != 0 else None

    cagr = None
    at_ini, at_fin = float(ativo.iloc[0]), float(ativo.iloc[-1])
    n = len(cols_dates) - 1
    if n > 0 and at_ini > 0:
        cagr = (at_fin / at_ini) ** (1 / n) - 1

    linhas = [
        f"EMPRESA: {empresa}",
        f"ESCALA: {scale_option}",
        f"PERÍODOS ANALISADOS: {', '.join(cols_dates)}",
        f"ÚLTIMO PERÍODO: {ultimo}",
        "",
        "=== ESTRUTURA PATRIMONIAL (último período) ===",
        f"  Ativo Total:          {v(ativo):,.2f}" if v(ativo) else "  Ativo Total: N/D",
        f"  Ativo Circulante:     {v(ativo_c):,.2f}" if v(ativo_c) else "  Ativo Circulante: N/D",
        f"  Ativo Não Circulante: {v(ativo_nc):,.2f}" if v(ativo_nc) else "  Ativo N. Circ.: N/D",
        f"  Passivo Circulante:   {v(pass_c):,.2f}" if v(pass_c) else "  Passivo Circulante: N/D",
        f"  Passivo N. Circ.:     {v(pass_nc):,.2f}" if v(pass_nc) else "  Passivo N. Circ.: N/D",
        f"  Patrimônio Líquido:   {v(pl):,.2f}" if v(pl) else "  Patrimônio Líquido: N/D",
        "",
        "=== CRESCIMENTO DO ATIVO TOTAL ===",
    ]

    for dt in cols_dates:
        linhas.append(f"  {dt}: {float(ativo[dt]):,.2f}")

    if cagr is not None:
        linhas.append(f"\n  CAGR do período: {cagr * 100:.1f}%")
    yoy_at = yoy(ativo)
    if yoy_at is not None:
        linhas.append(f"  Variação YoY (último): {yoy_at:+.1f}%")

    estrutura_note = ""
    va, vp = v(ativo), v(pl)
    if va and vp and va != 0:
        estrutura_note = f"\n  PL / Ativo Total: {vp / va * 100:.1f}%"
        linhas.append(estrutura_note)

    return "\n".join(linhas)


def _prompt_bp(contexto: str, empresa: str) -> str:
    return f"""
Analise o Balanço Patrimonial abaixo da empresa {empresa}.

{contexto}

Por favor, forneça:
1. **Estrutura de Capital** — composição do ativo e passivo, proporção de PL.
2. **Tendência do Ativo Total** — o que o CAGR e a variação YoY revelam.
3. **Riscos de Liquidez** — relação entre ativo circulante e passivo circulante.
4. **Alavancagem** — nível de endividamento e dependência de capital de terceiros.
5. **Conclusão** — resumo em 2 frases sobre a solidez patrimonial.

Seja conciso. Use bullet points nas seções 2, 3 e 4.
""".strip()


def build_context_dre(df_pivot: pd.DataFrame, cols_dates: list,
                      empresa: str, scale_option: str = "Milhões (MM)") -> str:
    """Constrói contexto textual para análise da DRE."""
    if df_pivot.empty or not cols_dates:
        return "Sem dados disponíveis."

    def get_row(code):
        r = df_pivot[df_pivot["CD_CONTA"] == code]
        return r[cols_dates].iloc[0].astype(float) if not r.empty else pd.Series(0.0, index=cols_dates)

    receita = get_row("3.01")
    cpv     = get_row("3.02")
    lb      = get_row("3.03")
    desp    = get_row("3.04")
    ebit    = get_row("3.05")
    res_fin = get_row("3.06")
    lair    = get_row("3.07")
    ll      = get_row("3.11")

    ultimo = cols_dates[-1]
    def v(s): return float(s[ultimo]) if ultimo in s.index else None
    def mg(num, den):
        vn, vd = v(num), v(den)
        return vn / vd * 100 if vn is not None and vd and vd != 0 else None

    # CAGR receita
    cagr = None
    r_ini, r_fin = float(receita.iloc[0]), float(receita.iloc[-1])
    n = len(cols_dates) - 1
    if n > 0 and r_ini != 0:
        cagr = (r_fin / r_ini) ** (1 / n) - 1

    linhas = [
        f"EMPRESA: {empresa}",
        f"ESCALA: {scale_option}",
        f"PERÍODOS: {', '.join(cols_dates)}",
        "",
        f"=== DRE — ÚLTIMO PERÍODO ({ultimo}) ===",
        f"  Receita Líquida (3.01):  {v(receita):,.2f}" if v(receita) else "  Receita: N/D",
        f"  CPV / CSP (3.02):        {v(cpv):,.2f}" if v(cpv) else "  CPV: N/D",
        f"  Lucro Bruto (3.03):      {v(lb):,.2f}" if v(lb) else "  L. Bruto: N/D",
        f"  Despesas Oper. (3.04):   {v(desp):,.2f}" if v(desp) else "  Desp: N/D",
        f"  EBIT (3.05):             {v(ebit):,.2f}" if v(ebit) else "  EBIT: N/D",
        f"  Res. Financeiro (3.06):  {v(res_fin):,.2f}" if v(res_fin) else "  Res. Fin.: N/D",
        f"  LAIR (3.07):             {v(lair):,.2f}" if v(lair) else "  LAIR: N/D",
        f"  Lucro Líquido (3.11):    {v(ll):,.2f}" if v(ll) else "  Lucro Líq.: N/D",
        "",
        "=== MARGENS (último período) ===",
        f"  Margem Bruta:    {mg(lb, receita):.1f}%" if mg(lb, receita) is not None else "  Margem Bruta: N/D",
        f"  Margem EBIT:     {mg(ebit, receita):.1f}%" if mg(ebit, receita) is not None else "  Margem EBIT: N/D",
        f"  Margem Líquida:  {mg(ll, receita):.1f}%" if mg(ll, receita) is not None else "  Margem Líq.: N/D",
        "",
        "=== EVOLUÇÃO DA RECEITA ===",
    ]
    for dt in cols_dates:
        linhas.append(f"  {dt}: {float(receita[dt]):,.2f}")
    if cagr is not None:
        linhas.append(f"\n  CAGR Receita: {cagr * 100:.1f}%")

    return "\n".join(linhas)


def _prompt_dre(contexto: str, empresa: str) -> str:
    return f"""
Analise a Demonstração do Resultado do Exercício (DRE) abaixo da empresa {empresa}.

{contexto}

Por favor, forneça:
1. **Qualidade do Resultado** — as margens são saudáveis para o setor?
2. **Evolução da Receita** — o que o CAGR e a trajetória histórica revelam?
3. **Eficiência Operacional** — análise do CPV, despesas e EBIT.
4. **Resultado Financeiro** — o impacto do endividamento no resultado.
5. **Conclusão** — síntese em 2 frases sobre a rentabilidade da empresa.

Seja conciso. Use bullet points nas seções 2, 3 e 4.
""".strip()


def build_context_dfc(df_pivot: pd.DataFrame, cols_dates: list,
                      empresa: str, scale_option: str = "Milhões (MM)") -> str:
    """Constrói contexto textual para análise da DFC."""
    if df_pivot.empty or not cols_dates:
        return "Sem dados disponíveis."

    def get_row(code):
        r = df_pivot[df_pivot["CD_CONTA"] == code]
        return r[cols_dates].iloc[0].astype(float) if not r.empty else pd.Series(0.0, index=cols_dates)

    fco = get_row("6.01")
    fci = get_row("6.02")
    fcf_fin = get_row("6.03")
    fcf_livre = fco + fci

    ultimo = cols_dates[-1]
    def v(s): return float(s[ultimo]) if ultimo in s.index else None

    linhas = [
        f"EMPRESA: {empresa}",
        f"ESCALA: {scale_option}",
        f"PERÍODOS: {', '.join(cols_dates)}",
        "",
        f"=== DFC — ÚLTIMO PERÍODO ({ultimo}) ===",
        f"  FCO — Operacional (6.01):    {v(fco):,.2f}" if v(fco) is not None else "  FCO: N/D",
        f"  FCI — Investimento (6.02):   {v(fci):,.2f}" if v(fci) is not None else "  FCI: N/D",
        f"  FCF — Financiamento (6.03):  {v(fcf_fin):,.2f}" if v(fcf_fin) is not None else "  FCF Fin.: N/D",
        f"  Free Cash Flow (FCO+FCI):    {v(fcf_livre):,.2f}" if v(fcf_livre) is not None else "  FCF Livre: N/D",
        "",
        "=== EVOLUÇÃO DO FCO OPERACIONAL ===",
    ]
    for dt in cols_dates:
        linhas.append(f"  {dt}: {float(fco[dt]):,.2f}")

    linhas += [
        "",
        "=== EVOLUÇÃO DO FREE CASH FLOW ===",
    ]
    for dt in cols_dates:
        linhas.append(f"  {dt}: {float(fcf_livre[dt]):,.2f}")

    return "\n".join(linhas)


def _prompt_dfc(contexto: str, empresa: str) -> str:
    return f"""
Analise a Demonstração dos Fluxos de Caixa (DFC) abaixo da empresa {empresa}.

{contexto}

Por favor, forneça:
1. **Geração de Caixa Operacional** — o FCO é positivo e crescente? A empresa gera caixa sustentável?
2. **Política de Investimentos** — o FCI indica expansão, manutenção ou desinvestimento?
3. **Estrutura de Financiamento** — o FCF de financiamento indica captação ou amortização de dívidas?
4. **Free Cash Flow** — a empresa sobra caixa após investir? Qual a tendência?
5. **Conclusão** — saúde de caixa em 2 frases.

Seja conciso. Use bullet points nas seções 2, 3 e 4.
""".strip()


def build_context_vs_todos_setores(df_all: pd.DataFrame, emp_row,
                                   nome_empresa: str, data_ref: str) -> str:
    """Contexto para análise de empresa frente a todos os setores."""
    indicadores = {
        "MARGEM_LIQUIDA":     ("Margem Líquida",  "pct"),
        "MARGEM_BRUTA":       ("Margem Bruta",    "pct"),
        "ROE":                ("ROE",             "pct"),
        "ROA":                ("ROA",             "pct"),
        "LIQUIDEZ_CORRENTE":  ("Liq. Corrente",   "num"),
        "ENDIVIDAMENTO_GERAL":("Endividamento",   "pct"),
    }

    linhas = [
        f"EMPRESA vs TODOS OS SETORES — PERÍODO: {data_ref}",
        f"Empresa: {nome_empresa}",
        "",
        "=== INDICADORES DA EMPRESA ===",
    ]
    for col, (label, tipo) in indicadores.items():
        v_raw = emp_row.get(col, None)
        v = None if v_raw is None or (isinstance(v_raw, float) and np.isnan(v_raw)) else float(v_raw)
        linhas.append(f"  {label}: {_fmt(v, tipo)}")

    if "SETOR" in df_all.columns:
        linhas += ["", "=== MEDIANAS POR SETOR ===",
                   f"  {'SETOR':<35} {'Mg.Líq.':>10} {'ROE':>8} {'Liq.Cor.':>10} {'Endivid.':>11}"]
        cols_ok = {c for c in indicadores if c in df_all.columns}
        for _, row in df_all.sort_values("SETOR").iterrows():
            ml  = _fmt(row.get("MARGEM_LIQUIDA"), "pct") if "MARGEM_LIQUIDA" in cols_ok else "N/D"
            roe = _fmt(row.get("ROE"), "pct")             if "ROE" in cols_ok else "N/D"
            lc  = _fmt(row.get("LIQUIDEZ_CORRENTE"), "num") if "LIQUIDEZ_CORRENTE" in cols_ok else "N/D"
            eg  = _fmt(row.get("ENDIVIDAMENTO_GERAL"), "pct") if "ENDIVIDAMENTO_GERAL" in cols_ok else "N/D"
            setor = str(row.get("SETOR", ""))[:35]
            linhas.append(f"  {setor:<35} {ml:>10} {roe:>8} {lc:>10} {eg:>11}")

    return "\n".join(linhas)


def _prompt_vs_todos_setores(contexto: str, empresa: str) -> str:
    return f"""
Analise o posicionamento da empresa {empresa} frente a todos os setores da CVM abaixo.

{contexto}

Por favor, forneça:
1. **Posicionamento Relativo** — em quais indicadores a empresa se destaca positiva ou negativamente frente aos setores?
2. **Setores Comparáveis** — quais setores possuem perfil financeiro mais similar à empresa?
3. **Vantagens Competitivas** — onde a empresa supera a mediana da maioria dos setores?
4. **Vulnerabilidades** — onde a empresa fica abaixo da maioria dos setores?
5. **Conclusão** — síntese do posicionamento relativo em 2 frases.

Seja conciso. Use bullet points nas seções 2, 3 e 4.
""".strip()




def render_ai_panel(
    contexto: str,
    prompt_fn,
    titulo: str = "🤖 Análise da IA (Groq)",
    panel_key: str = "ai_panel",
):
    """
    Renderiza o painel de análise de IA como um st.expander.

    Parâmetros
    ----------
    contexto  : string com os dados formatados para o prompt
    prompt_fn : callable(contexto) -> str  que monta o prompt final
    titulo    : título do expander
    panel_key : chave única do Streamlit para o botão
    """
    with st.expander(titulo, expanded=False):
        # Verifica disponibilidade antes de mostrar o botão
        _, err_cfg = _get_groq_client()
        if err_cfg:
            st.info(
                f"💡 **Análise de IA indisponível:** {err_cfg}\n\n"
                "Para habilitar, adicione `GROQ_API_KEY=sua_chave` no arquivo `.env` "
                "e reinicie o dashboard. Chave gratuita em [console.groq.com](https://console.groq.com)."
            )
            return

        st.caption("Powered by **Groq** · modelo `llama-3.3-70b-versatile`")

        col_btn, col_warn = st.columns([1, 4])
        with col_btn:
            analisar = st.button("▶ Analisar", key=f"btn_{panel_key}")

        if analisar:
            with st.spinner("Consultando a IA..."):
                prompt_final = prompt_fn(contexto)
                texto, err = _call_groq(
                    system_prompt=_SYSTEM_BASE,
                    user_prompt=prompt_final,
                )

            if err:
                st.warning(f"⚠️ Não foi possível gerar a análise: {err}")
            elif texto:
                st.markdown("---")
                st.markdown(texto)
                st.caption("⚠️ Esta análise é gerada por IA e tem fins exclusivamente didáticos. "
                           "Não constitui recomendação de investimento.")
