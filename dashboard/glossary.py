
GLOSSARIO: dict[str, dict] = {

    # ------------------------------------------------------------------
    # RENTABILIDADE
    # ------------------------------------------------------------------
    "MARGEM_BRUTA": {
        "label":   "Margem Bruta",
        "formula": "Lucro Bruto ÷ Receita Líquida",
        "ref":     "Varia muito por setor; varejo ~20–40%, tecnologia pode passar de 60%.",
        "tip":     "Mede o quanto sobra após os custos diretos de produção ou serviço. "
                   "Quanto maior, maior a capacidade de absorver despesas operacionais e gerar lucro.",
    },
    "MARGEM_EBIT": {
        "label":   "Margem EBIT",
        "formula": "EBIT ÷ Receita Líquida",
        "ref":     "Referência saudável: acima de 10% na maioria dos setores.",
        "tip":     "Também chamada de Margem Operacional. Mostra a eficiência do negócio antes de "
                   "juros e imposto de renda — isola o resultado das decisões de financiamento.",
    },
    "MARGEM_LIQUIDA": {
        "label":   "Margem Líquida",
        "formula": "Lucro Líquido ÷ Receita Líquida",
        "ref":     "Boas empresas industriais ficam entre 5–15%; tecnologia pode superar 20%.",
        "tip":     "O quanto de cada R$ de receita se transforma em lucro final após todos os custos, "
                   "despesas, juros e impostos. Principal indicador de rentabilidade final.",
    },
    "ROA": {
        "label":   "ROA",
        "formula": "Lucro Líquido ÷ Ativo Total",
        "ref":     "Acima de 5% é considerado bom; bancos costumam ter ROA entre 1–2%.",
        "tip":     "Return on Assets — retorno gerado sobre cada real de ativo. "
                   "Mede a eficiência com que a empresa usa seus recursos para gerar lucro.",
    },
    "ROE": {
        "label":   "ROE",
        "formula": "Lucro Líquido ÷ Patrimônio Líquido",
        "ref":     "Acima de 15% é considerado atrativo; compare sempre com o custo de capital (WACC/Ke).",
        "tip":     "Return on Equity — retorno sobre o capital dos acionistas. "
                   "Quanto maior, mais eficientemente a empresa remunera quem investiu. "
                   "Valores muito altos podem indicar alta alavancagem — analise junto ao endividamento.",
    },
    "ROIC": {
        "label":   "ROIC",
        "formula": "NOPAT ÷ Capital Investido",
        "ref":     "ROIC > WACC indica geração de valor; < WACC destrói valor.",
        "tip":     "Return on Invested Capital — retorno sobre o capital total investido (PL + Dívida Líquida). "
                   "É o indicador mais completo de criação de valor.",
    },

    # ------------------------------------------------------------------
    # LIQUIDEZ
    # ------------------------------------------------------------------
    "LIQUIDEZ_CORRENTE": {
        "label":   "Liquidez Corrente",
        "formula": "Ativo Circulante ÷ Passivo Circulante",
        "ref":     "Ideal ≥ 1,0. Entre 1,5–2,0 é considerado confortável.",
        "tip":     "Capacidade de pagar todas as obrigações de curto prazo com os ativos circulantes. "
                   "< 1,0 indica que o passivo circulante supera o ativo — sinal de alerta de liquidez.",
    },
    "LIQUIDEZ_SECA": {
        "label":   "Liquidez Seca",
        "formula": "(Ativo Circulante − Estoques) ÷ Passivo Circulante",
        "ref":     "Ideal ≥ 0,8. Mais exigente que a corrente.",
        "tip":     "Versão conservadora da Liquidez Corrente: exclui os estoques (ativo menos líquido). "
                   "Mostra a capacidade de pagamento sem precisar vender estoque.",
    },
    "LIQUIDEZ_IMEDIATA": {
        "label":   "Liquidez Imediata",
        "formula": "Caixa e Equivalentes ÷ Passivo Circulante",
        "ref":     "Muito baixo varia por setor; não precisa ser alto se o ciclo financeiro for curto.",
        "tip":     "Capacidade de quitar obrigações de curto prazo usando apenas o caixa disponível. "
                   "Valores muito altos podem indicar excesso de caixa ocioso.",
    },
    "LIQUIDEZ_GERAL": {
        "label":   "Liquidez Geral",
        "formula": "(AC + ARLP) ÷ (PC + PNC)",
        "ref":     "Ideal ≥ 1,0 no longo prazo.",
        "tip":     "Visão de longo prazo: considera também os ativos e passivos não circulantes. "
                   "Mostra a saúde financeira estrutural da empresa.",
    },

    # ------------------------------------------------------------------
    # ENDIVIDAMENTO
    # ------------------------------------------------------------------
    "ENDIVIDAMENTO_GERAL": {
        "label":   "Endividamento Geral",
        "formula": "Passivo Total ÷ Ativo Total",
        "ref":     "< 50% é conservador; > 70% pode ser preocupante dependendo do setor.",
        "tip":     "Proporção do ativo total financiada por capital de terceiros. "
                   "Quanto maior, mais alavancada e dependente de dívida é a empresa.",
    },
    "GRAU_ENDIVIDAMENTO": {
        "label":   "Grau de Endividamento",
        "formula": "Passivo Total ÷ Patrimônio Líquido",
        "ref":     "< 1,0 significa que há mais capital próprio que de terceiros.",
        "tip":     "Quantos reais de capital de terceiros existem para cada real de capital próprio. "
                   "Empresas muito alavancadas têm grau > 2,0.",
    },
    "COMPOSICAO_ENDIVIDAMENTO": {
        "label":   "Composição do Endividamento",
        "formula": "Passivo Circulante ÷ (PC + PNC)",
        "ref":     "Quanto menor, melhor: indica que a dívida tem prazo mais longo para vencer.",
        "tip":     "Proporção da dívida total que vence no curto prazo. "
                   "Valores altos indicam maior pressão sobre o caixa no curto prazo.",
    },
    "DIVIDA_LIQUIDA": {
        "label":   "Dívida Líquida",
        "formula": "Dívida Bruta − Caixa e Aplicações",
        "ref":     "Negativa indica caixa líquido (empresa tem mais caixa que dívida).",
        "tip":     "Endividamento real da empresa descontando o caixa disponível. "
                   "É o principal indicador usado em valuation (EV = Market Cap + Dívida Líquida).",
    },
    "COBERTURA_JUROS": {
        "label":   "Cobertura de Juros",
        "formula": "EBIT ÷ Despesas Financeiras",
        "ref":     "≥ 3x é confortável; < 1,5x acende alerta de insolvência.",
        "tip":     "Quantas vezes o resultado operacional cobre os juros da dívida. "
                   "Quanto maior, mais segura é a posição financeira.",
    },

    # ------------------------------------------------------------------
    # CICLOS OPERACIONAIS
    # ------------------------------------------------------------------
    "PMRV": {
        "label":   "PMRV",
        "formula": "(Contas a Receber ÷ Receita Bruta) × 360",
        "ref":     "Depende do setor; varejo à vista tem PMRV próximo de zero; B2B pode ter 60–90 dias.",
        "tip":     "Prazo Médio de Recebimento de Vendas — quantos dias, em média, a empresa leva "
                   "para receber de seus clientes após a venda. Menor PMRV = menos capital imobilizado.",
    },
    "PME": {
        "label":   "PME",
        "formula": "(Estoques ÷ CPV) × 360",
        "ref":     "Varia muito por setor; alimentos perecíveis ~7 dias; máquinas pesadas pode passar de 180.",
        "tip":     "Prazo Médio de Estocagem — quantos dias os produtos ficam em estoque antes de serem vendidos. "
                   "Menor PME = giro mais rápido de estoques = menos capital parado.",
    },
    "PMPF": {
        "label":   "PMPF",
        "formula": "(Fornecedores ÷ CPV) × 360",
        "ref":     "Quanto maior, melhor: a empresa financia parte do giro com capital do fornecedor.",
        "tip":     "Prazo Médio de Pagamento a Fornecedores — quantos dias a empresa leva para pagar seus fornecedores. "
                   "PMPF alto reduz a necessidade de capital de giro próprio.",
    },
    "CICLO_OPERACIONAL": {
        "label":   "Ciclo Operacional",
        "formula": "PMRV + PME",
        "ref":     "Quanto menor, mais eficiente o ciclo de geração de caixa.",
        "tip":     "Tempo total desde a compra de insumos/matéria-prima até o recebimento da venda. "
                   "Reflete a eficiência operacional como um todo.",
    },
    "CICLO_FINANCEIRO": {
        "label":   "Ciclo Financeiro",
        "formula": "Ciclo Operacional − PMPF",
        "ref":     "CF negativo é excelente (ex: grandes varejistas) — a empresa recebe antes de pagar.",
        "tip":     "Período em que a empresa precisa financiar o giro com recursos próprios ou dívida. "
                   "CF negativo significa que fornecedores financiam o ciclo (modelo de capital de giro negativo).",
    },

    # ------------------------------------------------------------------
    # CAPITAL DE GIRO
    # ------------------------------------------------------------------
    "NCG": {
        "label":   "NCG",
        "formula": "AC operacional − PC operacional",
        "ref":     "NCG > 0 exige capital; NCG < 0 indica que o modelo gera caixa naturalmente.",
        "tip":     "Necessidade de Capital de Giro — recursos permanentes que o ciclo operacional exige. "
                   "Empresas com NCG alta e crescente podem ter problemas de caixa mesmo sendo lucrativas.",
    },
    "CGL": {
        "label":   "CGL",
        "formula": "Ativo Circulante − Passivo Circulante",
        "ref":     "CGL positivo indica folga financeira de curto prazo.",
        "tip":     "Capital de Giro Líquido — diferença entre ativos e passivos de curto prazo. "
                   "Indica a folga financeira disponível para operações do dia a dia.",
    },
    "CGP": {
        "label":   "CGP",
        "formula": "PL + Passivo NC − Ativo NC",
        "ref":     "CGP > NCG é o cenário ideal (funding permanente cobre a necessidade).",
        "tip":     "Capital de Giro Permanente — parte do capital permanente (PL + dívida LP) "
                   "direcionada ao financiamento do giro. Deve ser ≥ NCG para equilíbrio financeiro.",
    },
    "ST": {
        "label":   "Saldo de Tesouraria",
        "formula": "CGL − NCG",
        "ref":     "ST < 0 é sinal de alerta: a empresa usa recursos de curto prazo para financiar o giro.",
        "tip":     "Saldo de Tesouraria — folga (ou déficit) entre o capital de giro disponível e o necessário. "
                   "ST crescentemente negativo é o sinal clássico do 'Efeito Tesoura' (crescimento sem caixa).",
    },

    # ------------------------------------------------------------------
    # VARIÁVEIS CONTÁBEIS (V00–V23)
    # ------------------------------------------------------------------
    "V00": {"label": "Ativo Total", "formula": "AC + ANC",
             "ref": "", "tip": "Soma de todos os recursos controlados pela empresa (circulantes + não circulantes)."},
    "V01": {"label": "Ativo Circulante", "formula": "Caixa + Recebíveis + Estoques + Outros AC",
             "ref": "", "tip": "Ativos que se convertem em caixa em até 12 meses."},
    "V02": {"label": "Caixa e Equiv.", "formula": "—",
             "ref": "", "tip": "Recursos imediatamente disponíveis: caixa, contas bancárias e aplicações com liquidez imediata."},
    "V16": {"label": "Receita Líquida", "formula": "Receita Bruta − Devoluções − Impostos s/ Vendas",
             "ref": "", "tip": "Faturamento efetivo após deduções. Base para cálculo de todas as margens."},
    "V17": {"label": "CPV / CSP", "formula": "—",
             "ref": "", "tip": "Custo dos Produtos Vendidos ou Serviços Prestados — custo direto de geração da receita."},
    "V18": {"label": "Lucro Bruto", "formula": "Receita Líquida − CPV",
             "ref": "", "tip": "Resultado após os custos diretos. Base da Margem Bruta."},
    "V20": {"label": "EBIT", "formula": "Lucro Bruto − Despesas Operacionais",
             "ref": "", "tip": "Earnings Before Interest and Taxes — lucro operacional, base da Margem EBIT."},
    "V23": {"label": "Lucro Líquido", "formula": "LAIR − IR/CSLL",
             "ref": "", "tip": "Resultado final após todos os custos, despesas, juros e impostos."},
}


def tooltip(col: str) -> str | None:
    """Retorna a string de tooltip formatada para o parâmetro `help=` do Streamlit."""
    entry = GLOSSARIO.get(col)
    if not entry:
        return None

    partes = []
    if entry.get("formula"):
        partes.append(f"**📐 Fórmula:** {entry['formula']}")
    if entry.get("tip"):
        partes.append(f"**💡 O que é:** {entry['tip']}")
    if entry.get("ref"):
        partes.append(f"**📊 Referência:** {entry['ref']}")

    return "\n\n".join(partes) if partes else None


def label(col: str, fallback: str = "") -> str:
    """Retorna o nome curto do indicador."""
    return GLOSSARIO.get(col, {}).get("label", fallback)


# ------------------------------------------------------------------
# TOOLTIPS DE GRÁFICOS
# ------------------------------------------------------------------

GRAFICOS: dict[str, str] = {

    # ── Indicadores Financeiros ────────────────────────────────────
    "grafico_resultado": (
        "**Receita Líquida vs Lucro Líquido**\n\n"
        "As barras mostram o faturamento real (receita líquida) a cada período. "
        "A linha roxa sobreposta indica o lucro líquido — o que efetivamente sobrou após todos os "
        "custos, despesas, juros e impostos.\n\n"
        "**Como ler:** Quando a linha do lucro cresce proporcionalmente à receita, a empresa está "
        "melhorando sua eficiência. Se a receita cresce mas o lucro estagna ou cai, há pressão "
        "de custos ou despesas financeiras."
    ),
    "grafico_margens": (
        "**Evolução das Margens**\n\n"
        "Mostra a trajetória histórica das principais margens de rentabilidade:\n\n"
        "- **Margem Bruta** — eficiência na produção/serviço\n"
        "- **Margem EBIT** — eficiência operacional (antes de juros e IR)\n"
        "- **Margem Líquida** — rentabilidade final\n"
        "- **ROA / ROE** — retorno sobre ativos e patrimônio\n\n"
        "**Como ler:** Margens em expansão indicam ganho de eficiência ou poder de precificação. "
        "Margens comprimidas podem sinalizar aumento de custos ou pressão competitiva."
    ),
    "grafico_composicao_ativo": (
        "**Composição do Ativo Total**\n\n"
        "Barras empilhadas mostrando como o ativo total se distribui entre as principais categorias "
        "(caixa, recebíveis, estoques, imobilizado, intangível, etc.) ao longo do tempo.\n\n"
        "**Como ler:** Uma empresa com ativo muito concentrado em imobilizado é intensiva em capital. "
        "Ativos líquidos (caixa e recebíveis) elevados indicam maior flexibilidade financeira. "
        "Mudanças na composição revelam decisões estratégicas de alocação de capital."
    ),
    "grafico_intangivel": (
        "**Intangível sobre Ativo Total**\n\n"
        "As barras mostram o valor absoluto do ativo intangível (marcas, patentes, softwares, goodwill). "
        "A linha dourada indica qual percentual ele representa do ativo total.\n\n"
        "**Como ler:** Participação crescente de intangíveis pode refletir aquisições pagas com ágio "
        "(goodwill) ou investimento em propriedade intelectual. Valores muito altos merecem atenção, "
        "pois intangíveis podem ser impactados por testes de impairment."
    ),
    "grafico_ncg": (
        "**Necessidade de Capital de Giro (NCG)**\n\n"
        "- **NCG** — quanto capital o ciclo operacional exige permanentemente\n"
        "- **Saldo de Tesouraria (ST)** — folga (ou déficit) entre CGL e NCG\n"
        "- **CGL** — Capital de Giro Líquido (AC − PC)\n"
        "- **CGP** — Capital de Giro Permanente (PL + Dívida LP − ANC)\n\n"
        "**Como ler:** ST crescentemente negativo é o sinal clássico do 'Efeito Tesoura' — "
        "a empresa cresce mas deteriora sua posição de caixa. "
        "CGP ≥ NCG é o cenário de equilíbrio financeiro saudável."
    ),

    # ── DRE ───────────────────────────────────────────────────────
    "waterfall_dre": (
        "**Cascata do Resultado (Waterfall)**\n\n"
        "Decompõe a jornada da receita até o lucro líquido, mostrando o impacto de cada linha da DRE:\n\n"
        "- 🟢 Barras positivas — entradas ou resultados favoráveis\n"
        "- 🔴 Barras negativas — custos e despesas que consomem a receita\n\n"
        "**Como ler:** Visualize quanto de cada R$ de receita é consumido em cada etapa. "
        "Uma cascata com muitas barras vermelhas grandes indica empresa de margens apertadas."
    ),
    "margens_dre": (
        "**Margens Históricas (DRE)**\n\n"
        "Evolução temporal das três principais margens calculadas diretamente das contas da DRE:\n\n"
        "- **Margem Bruta** = Lucro Bruto ÷ Receita (3.03 ÷ 3.01)\n"
        "- **Margem EBIT** = EBIT ÷ Receita (3.05 ÷ 3.01)\n"
        "- **Margem Líquida** = Lucro Líquido ÷ Receita (3.11 ÷ 3.01)\n\n"
        "**Como ler:** O spread entre Margem Bruta e EBIT revela o peso das despesas operacionais. "
        "O spread entre EBIT e Líquida revela o custo da dívida (resultado financeiro + IR)."
    ),
    "evolucao_resultado_dre": (
        "**Evolução Temporal — Receita, Lucro Bruto, EBIT e Lucro Líquido**\n\n"
        "Compara a trajetória das principais linhas da DRE no mesmo gráfico.\n\n"
        "**Como ler:** Quando as linhas se aproximam, os custos e despesas estão crescendo mais que a "
        "receita. Linhas paralelas indicam estrutura de custos estável. "
        "EBIT e Lucro divergindo muito sugere alto custo financeiro (dívida)."
    ),
    "crescimento_receita_dre": (
        "**Crescimento da Receita com CAGR**\n\n"
        "- Barras superiores: receita líquida absoluta por período\n"
        "- Barras inferiores: variação percentual YoY (ano a ano)\n"
        "- **CAGR** (título) = taxa de crescimento anual composta do período selecionado\n\n"
        "**Como ler:** CAGR acima da inflação indica crescimento real. "
        "Variações YoY erráticas (altos e baixos) sugerem negócio cíclico ou instável."
    ),
    "funil_margens_dre": (
        "**Funil de Margens (último período)**\n\n"
        "Visualização em funil mostrando como a receita vai sendo consumida até chegar ao lucro líquido. "
        "Cada barra exibe o valor absoluto e o percentual sobre a receita.\n\n"
        "**Como ler:** Quanto mais 'aberto' o funil (pouca perda entre etapas), maior a eficiência. "
        "Um funil muito estreito no final indica empresa de margens comprimidas."
    ),
    "custo_receita_dre": (
        "**Decomposição de Custos sobre Receita**\n\n"
        "Área empilhada mostrando quanto cada categoria de custo representa da receita ao longo do tempo:\n\n"
        "- **CPV/CSP** — custo direto de produção/serviço\n"
        "- **Despesas Operacionais** — vendas, administrativas, P&D\n"
        "- **Resultado Financeiro** — juros e encargos da dívida\n"
        "- **IR/CSLL** — tributos sobre o lucro\n\n"
        "**Como ler:** Linha total acima de 100% indica prejuízo. "
        "Veja qual categoria mais cresce ao longo do tempo — ela é o principal risco de margem."
    ),

    # ── Balanço Patrimonial ────────────────────────────────────────
    "sunburst_bp": (
        "**Estrutura Patrimonial (Sunburst)**\n\n"
        "Gráfico de anéis interativo mostrando a proporção de cada grupo patrimonial. "
        "Clique nos segmentos para expandir e ver as subcontas.\n\n"
        "- **Ativo** (verde) — recursos controlados pela empresa\n"
        "- **Passivo + PL** (azul) — financiamento desses recursos\n\n"
        "**Como ler:** O tamanho de cada fatia revela a importância relativa de cada grupo. "
        "Passivo Circulante muito grande em relação ao Ativo Circulante pode indicar pressão de liquidez."
    ),
    "evolucao_ativo_bp": (
        "**Evolução da Composição do Ativo**\n\n"
        "Área empilhada mostrando como as categorias do ativo evoluem ao longo dos períodos selecionados.\n\n"
        "**Como ler:** Crescimento do Caixa indica geração de valor. "
        "Crescimento acelerado de Recebíveis pode sinalizar problemas de cobrança ou política de crédito agressiva. "
        "Imobilizado crescente indica expansão de capacidade produtiva."
    ),
    "estrutura_capital_bp": (
        "**Estrutura de Capital — Ativo vs Passivo**\n\n"
        "Barras divergentes: Ativo (acima do zero) vs Passivo + PL (abaixo do zero). "
        "Em um balanço equilibrado, as barras se igualam em magnitude.\n\n"
        "- **Ativo Circulante** — conversível em caixa em até 12 meses\n"
        "- **Ativo Não Circulante** — imobilizado, intangível, investimentos LP\n"
        "- **Passivo Circulante** — obrigações de curto prazo\n"
        "- **Passivo Não Circulante** — dívidas de longo prazo\n"
        "- **Patrimônio Líquido** — capital dos sócios\n\n"
        "**Como ler:** PL crescente indica acúmulo de resultados (empresa lucrativa e sólida). "
        "Passivo Circulante maior que o Ativo Circulante é sinal de alerta de liquidez."
    ),
    "validacao_crescimento_bp": (
        "**Equilíbrio Patrimonial e Crescimento do Ativo**\n\n"
        "- Barras superiores: Ativo Total (positivo) vs Passivo+PL (negativo) — devem se igualar\n"
        "- Linha inferior: variação percentual YoY do Ativo Total\n"
        "- **CAGR** (título) = crescimento anual composto do ativo no período selecionado\n\n"
        "**Como ler:** Divergência entre as barras indica erro nos dados ou diferença contábil. "
        "CAGR do ativo acima da inflação indica crescimento real patrimonial."
    ),

    # ── DFC ───────────────────────────────────────────────────────
    "fluxos_dfc": (
        "**Fluxos de Caixa por Atividade**\n\n"
        "Compara os três grandes blocos da DFC lado a lado:\n\n"
        "- 🟢 **FCO** — caixa gerado pelas operações do negócio (o mais importante)\n"
        "- 🔴 **FCI** — caixa usado em investimentos (capex, aquisições)\n"
        "- 🔵 **FCF** — caixa de financiamentos (captação ou pagamento de dívidas/dividendos)\n\n"
        "**Como ler:** Uma empresa saudável tem FCO positivo e crescente. "
        "FCI negativo é normal (empresa investindo). FCF negativo pode indicar amortização de dívidas (positivo) "
        "ou pagamento de dividendos."
    ),
    "cascata_caixa_dfc": (
        "**Composição da Variação de Caixa (Waterfall)**\n\n"
        "Mostra como FCO, FCI e FCF se somam para resultar na variação líquida de caixa do período.\n\n"
        "**Como ler:** A barra final (Variação Líquida) representa o saldo que entrou ou saiu do caixa. "
        "Variação negativa recorrente esgota as reservas de caixa ao longo do tempo."
    ),
    "fcf_dfc": (
        "**Free Cash Flow (FCF = FCO − |FCI|)**\n\n"
        "- Barras: FCO (caixa operacional) — o 'motor' que gera caixa\n"
        "- Linha: Free Cash Flow = FCO + FCI (FCI é geralmente negativo)\n\n"
        "**Como ler:** FCF positivo significa que a empresa gera caixa após os investimentos — "
        "pode pagar dividendos, amortizar dívidas ou acumular caixa. "
        "FCF negativo pode ser aceitável em fases de expansão acelerada, mas não de forma indefinida."
    ),
    "caixa_acumulado_dfc": (
        "**FCO Acumulado no Período Analisado**\n\n"
        "- Barras: FCO de cada período individualmente\n"
        "- Linha roxa: FCO acumulado desde o início do período selecionado\n\n"
        "**Como ler:** A área sob a linha roxa representa o total de caixa operacional gerado. "
        "Tendência crescente indica que o negócio se torna progressivamente mais gerador de caixa."
    ),
    "bolha_fco_fci_dfc": (
        "**FCO vs FCI — Dispersão Temporal**\n\n"
        "Cada bolha representa um período. O tamanho da bolha é proporcional ao Free Cash Flow (FCF).\n\n"
        "- 🟢 Verde — FCO positivo e FCI negativo (situação saudável: gera e investe)\n"
        "- 🔴 Vermelho — FCO negativo (alerta: operações não geram caixa)\n\n"
        "**Como ler:** Quadrante superior-direito (FCO+ / FCI+) indica desinvestimento. "
        "Quadrante inferior-direito (FCO+ / FCI−) é o ideal: empresa que gera e investe."
    ),
}


def chart_tooltip(grafico: str) -> str | None:
    """Retorna o texto de tooltip para o título de um gráfico (`help=` do st.subheader)."""
    return GRAFICOS.get(grafico)
