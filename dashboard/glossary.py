
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
