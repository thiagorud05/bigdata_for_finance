import streamlit as st

# CSS injetado apenas quando a tela Sobre está ativa.
# Como o Streamlit re-injeta todo CSS a cada navegação, esse bloco só
# está presente no DOM quando sobre.py é renderizado — sem persistência
# indesejada nas outras telas.
_SOBRE_CSS = """
<style>
@media (max-width: 768px) {
    /* Força colunas a empilharem (100% de largura) — substitui a
       regra de 50% do app.py que é ideal para métricas, mas estreita
       demais para textos longos como os da tela Sobre.             */
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        min-width: 100% !important;
        max-width: 100% !important;
        width:     100% !important;
        flex:      1 1  100% !important;
    }
    /* Tabelas: scroll horizontal para não quebrar layout */
    table {
        display: block;
        overflow-x: auto;
        white-space: nowrap;
    }
    /* Blocos de código: scroll horizontal + fonte menor */
    pre {
        overflow-x: auto !important;
        white-space: pre !important;
        font-size: 0.78rem !important;
    }
}
</style>
"""


def render_sobre_page():
    st.markdown(_SOBRE_CSS, unsafe_allow_html=True)

    st.title("CVM Data Lake — Sobre o Projeto")
    st.caption("Disciplina: Big Data for Finance · FAE Centro Universitário")
    st.markdown("---")

    tab_visao, tab_arq, tab_telas, tab_indicadores, tab_ia, tab_tecnico, tab_fluxo = st.tabs([
        "Visão Geral",
        "Arquitetura",
        "Funcionalidades",
        "Indicadores",
        "IA Analyst",
        "Decisões Técnicas",
        "Fluxogramas",
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # VISÃO GERAL
    # ─────────────────────────────────────────────────────────────────────────
    with tab_visao:
        col_a, col_b = st.columns([3, 2], gap="large")

        with col_a:
            st.subheader("O problema")
            st.markdown("""
A **CVM (Comissão de Valores Mobiliários)** publica os demonstrativos financeiros de todas as empresas
abertas brasileiras — balanço patrimonial, DRE, DFC e muito mais.

O problema: esses dados chegam em **dezenas de arquivos CSV por ano**, com estruturas diferentes por tipo
de documento, sem padronização de contas entre empresas, e sem qualquer cálculo de indicadores.

Analisar uma empresa ou comparar setores exige horas de limpeza de dados, junções manuais e cálculos repetitivos.
            """)

            st.subheader("A solução")
            st.markdown("""
Um **pipeline completo de dados** que vai da coleta bruta até um dashboard interativo com IA:

- **Coleta automatizada** dos arquivos da CVM (DFP, ITR, FRE)
- **Camada Silver** com dados limpos e hierarquizados
- **Camada Gold** com 20+ indicadores financeiros calculados automaticamente
- **Dashboard interativo** com 6 telas analíticas e análise por IA
- **Comparativos** entre empresas e benchmarks setoriais
            """)

        with col_b:
            st.subheader("Destaques")
            st.markdown("""
| | |
|---|---|
| 📊 | **6 telas analíticas** |
| 🏦 | **Dados reais da CVM** |
| 🤖 | **IA com LLaMA 3.3 70B** |
| 📐 | **20+ indicadores calculados** |
| 🏭 | **Benchmarks por setor** |
| 📱 | **Responsivo para mobile** |
| 🗄️ | **Medallion Architecture** |
| ⚡ | **Cache inteligente por TTL** |
            """)

            st.subheader("Para quem")
            st.markdown("""
- Estudantes de finanças e ciência de dados
- Professores e pesquisadores
- Analistas que precisam comparar empresas listadas
- Qualquer pessoa que queira entender os dados da CVM
            """)

    # ─────────────────────────────────────────────────────────────────────────
    # ARQUITETURA
    # ─────────────────────────────────────────────────────────────────────────
    with tab_arq:
        st.subheader("Arquitetura Medallion")
        st.markdown("""
O projeto segue a **Medallion Architecture**, padrão consolidado em engenharia de dados para
organizar a qualidade e transformação progressiva dos dados em três camadas:
        """)

        col1, col2, col3 = st.columns(3, gap="medium")

        with col1:
            st.markdown("#### 🥉 Bronze — Dados Brutos")
            st.markdown("""
**Fonte:** CVM Open Data (API pública)

**O que contém:**
- Arquivos DFP (demonstrações anuais)
- Arquivos ITR (trimestrais)
- Cadastro de empresas (CAD)
- Referencial de empresas (FRE)
- Logs de coleta

**Formato:** CSV original da CVM, sem transformações

**Notebooks:** `01_bronze/`
            """)

        with col2:
            st.markdown("#### 🥈 Silver — Dados Tratados")
            st.markdown("""
**Transformações aplicadas:**
- Seleção de empresas de interesse
- Padronização de contas contábeis
- Hierarquia de grupos (1 → 1.01 → 1.01.01)
- Filtragem de demonstrativos consolidados
- Validação: Ativo = Passivo + PL

**Tabelas geradas:**
- `n0_empresas_selecionadas`
- `n1_dfp_cia_aberta_bp` (Balanço)
- `n1_dfp_cia_aberta_dre` (Resultado)
- `n1_dfp_cia_aberta_dfc` (Caixa)

**Notebooks:** `02_silver/`
            """)

        with col3:
            st.markdown("#### 🥇 Gold — Indicadores")
            st.markdown("""
**O que é calculado:**
- 5 indicadores de rentabilidade
- 4 de liquidez
- 3 de endividamento
- 5 de ciclos operacionais
- 4 de capital de giro (NCG, ST, CGL, CGP)

**Tabela gerada:**
- `mart_indicadores_financeiros`

**Calculado por:** empresa × período de referência

**Notebooks:** `03_gold/`
            """)

        st.markdown("---")
        st.subheader("Fluxo de dados")
        st.markdown("""
```
CVM (dados abertos)
    │
    ▼  [01_bronze] Coleta automática
Arquivos CSV brutos (PostgreSQL · layer_01_bronze)
    │
    ▼  [02_silver] Limpeza e normalização
Demonstrativos padronizados (PostgreSQL · layer_02_silver)
    │
    ▼  [03_gold] Cálculo de indicadores
Mart de KPIs (PostgreSQL · layer_03_gold)
    │
    ▼  [dashboard] Visualização + IA
Dashboard Streamlit → usuário final
```
        """)

        st.markdown("---")
        st.subheader("Stack Tecnológico")
        col_st1, col_st2 = st.columns(2, gap="large")

        with col_st1:
            st.markdown("**Pipeline & Backend**")
            st.markdown("""
| Tecnologia | Uso |
|---|---|
| **Python 3.10+** | Linguagem principal |
| **PostgreSQL** | Armazenamento das 3 camadas |
| **SQLAlchemy 2.0** | ORM e connection pool |
| **psycopg2** | Driver PostgreSQL |
| **pandas 2.0** | ETL, pivoting, agregações |
| **NumPy** | Cálculos numéricos, z-score |
| **python-dotenv** | Variáveis de ambiente |
            """)

        with col_st2:
            st.markdown("**Dashboard & IA**")
            st.markdown("""
| Tecnologia | Uso |
|---|---|
| **Streamlit ≥ 1.35** | Framework do dashboard |
| **Plotly ≥ 5.18** | Gráficos interativos |
| **Groq API** | Inferência LLM |
| **LLaMA 3.3 70B** | Modelo de análise financeira |
| **Jupyter Notebooks** | Exploração e pipeline ETL |
            """)

    # ─────────────────────────────────────────────────────────────────────────
    # FUNCIONALIDADES
    # ─────────────────────────────────────────────────────────────────────────
    with tab_telas:
        st.subheader("Funcionalidades por Tela")

        t1, t2, t3, t4, t5 = st.tabs([
            "Balanço Patrimonial",
            "DRE",
            "DFC",
            "Indicadores",
            "Comparativo",
        ])

        with t1:
            st.markdown("#### Balanço Patrimonial")
            st.markdown("Analisa a estrutura patrimonial da empresa ao longo do tempo.")
            col_a, col_b = st.columns(2, gap="medium")
            with col_a:
                st.markdown("""
**Controles do usuário:**
- Seleção de empresa
- Múltiplas datas de referência
- Nível de detalhe (1–5 níveis de hierarquia)
- Escala: Unidade / Mil / Milhão / Bilhão

**Gráficos:**
- **Sunburst** interativo — drill-down de Ativo e Passivo+PL
- **Composição do Ativo** — stacked area ao longo do tempo
- **Estrutura de Capital** — barras divergentes (Ativo ↑ vs Passivo+PL ↓)
- **Crescimento** — barras + linha de variação YoY
                """)
            with col_b:
                st.markdown("""
**Extras:**
- Tabela completa com contas hierarquizadas
- Linha de validação: Ativo − (Passivo + PL) deve ser ≈ 0
- CAGR calculado automaticamente
- Análise da IA: estrutura de capital, riscos, alavancagem
                """)

        with t2:
            st.markdown("#### DRE — Demonstração do Resultado")
            st.markdown("Analisa a formação do resultado (receitas → lucro) e evolução das margens.")
            col_a, col_b = st.columns(2, gap="medium")
            with col_a:
                st.markdown("""
**Gráficos:**
- **Waterfall** — da Receita ao Lucro Líquido (cascata)
- **Evolução de Margens** — Bruta, EBIT, Líquida, ROA, ROE
- **Evolução de Resultados** — valores absolutos
- **Crescimento de Receita** — barras + % YoY
                """)
            with col_b:
                st.markdown("""
**Gráficos (cont.):**
- **Funil de Margens** — percentual de cada margem sobre a receita
- **Decomposição de Custos** — stacked area (CPV%, Desp%, Fin%, IR%)
- Análise da IA: qualidade do resultado, eficiência operacional
                """)

        with t3:
            st.markdown("#### DFC — Demonstração do Fluxo de Caixa")
            st.markdown("Analisa a geração e uso de caixa nas três atividades.")
            col_a, col_b = st.columns(2, gap="medium")
            with col_a:
                st.markdown("""
**Gráficos:**
- **Fluxos por Atividade** — FCO 🟢 / FCI 🔴 / FCF 🔵 em barras agrupadas
- **Cascata de Caixa** — como os 3 fluxos formam a variação líquida
- **Free Cash Flow** — barras FCO + linha FCF (FCO + FCI)
- **FCO Acumulado** — evolução acumulada do caixa operacional
                """)
            with col_b:
                st.markdown("""
**Gráficos (cont.):**
- **Mapa FCO × FCI** — scatter com 4 quadrantes:
  - 🟢 Saudável (opera bem, investe)
  - 🔴 Alerta (queima caixa operacional)
  - 🔵 Desinvestimento (vende ativos)
- Análise da IA: sustentabilidade do caixa, capex, financiamento
                """)

        with t4:
            st.markdown("#### Indicadores Financeiros")
            st.markdown("Painel completo de KPIs calculados sobre a Gold Layer.")
            col_a, col_b = st.columns(2, gap="medium")
            with col_a:
                st.markdown("""
**Cards por grupo:**
- Rentabilidade (4 cards): Margem Líquida, ROE, Margem Bruta, EBIT
- Liquidez (4 cards): Liq. Corrente, Seca, Imediata, Endividamento
- Ciclos (5 cards): PMRV, PME, PMPF, Ciclo Operacional, Ciclo Financeiro

**Gauges (velocímetros):**
- Margem Líquida, ROE, Liquidez Corrente, Endividamento
- Zonas de cor: verde = bom, amarelo = atenção, vermelho = ruim
                """)
            with col_b:
                st.markdown("""
**Gráficos históricos:**
- Receita vs Lucro (barras + linha)
- Evolução de margens (5 séries)
- Composição do Ativo (stacked)
- Intangível sobre Ativo Total
- NCG, ST, CGL, CGP

**Extras:**
- Tabela com todos os 22 indicadores + download CSV
- Tooltips explicativos em cada card
- Análise da IA
                """)

        with t5:
            st.markdown("#### Comparativo de Empresas")
            st.markdown("Três modos de análise comparativa.")

            m1, m2, m3 = st.tabs([
                "Empresa vs Empresa",
                "Empresa vs Setor",
                "Empresa vs Todos os Setores",
            ])

            with m1:
                st.markdown("""
**Seleção:** 2–5 empresas + data de referência

**Gráficos:**
- **Radar** — 7 KPIs normalizados por empresa
- **Barras agrupadas** por grupo (Rentabilidade, Liquidez, Endividamento, Ciclos)
- **Evolução temporal** — Margem Líquida lado a lado
- **Tabela comparativa** — todos os indicadores com glossário integrado
- **Análise da IA** — pontos fortes, divergências, riscos
                """)

            with m2:
                st.markdown("""
**Seleção:** 1 empresa → setor detectado automaticamente

**Benchmark:** mediana do setor (calculada na Gold Layer)

**Gráficos:**
- **Radar** — empresa vs mediana do setor
- **Barras agrupadas** com bandas P25–P75 do setor (intervalo interquartil)
- **Scorecard** — 6 KPIs com delta vs mediana (+ lógica invertida para endividamento)
- **Evolução temporal** — Margem Líquida empresa vs mediana histórica do setor
- **Análise da IA**
                """)

            with m3:
                st.markdown("""
**Seleção:** 1 empresa → compara com todos os setores

**Gráficos:**
- **Heatmap Z-Score** em 5 abas (Rentabilidade, Liquidez, Endividamento, Ciclos, Todos)
  - Z-score negado para indicadores onde menor = melhor
  - Empresa destacada no topo (★)
  - Cores RdYlGn (vermelho → amarelo → verde)
- **Ranking por Indicador** — barras ordenadas por setor, com linha da empresa
- **Tabela completa** de todos os setores e indicadores
- **Análise da IA**
                """)

    # ─────────────────────────────────────────────────────────────────────────
    # INDICADORES
    # ─────────────────────────────────────────────────────────────────────────
    with tab_indicadores:
        st.subheader("Indicadores Financeiros Calculados")
        st.markdown("Todos calculados automaticamente a partir das contas CVM padronizadas.")
        st.markdown("---")

        col_r, col_l = st.columns(2, gap="large")

        with col_r:
            st.markdown("#### Rentabilidade")
            st.markdown("""
| Indicador | Fórmula | Bom quando |
|---|---|---|
| **Margem Bruta** | Lucro Bruto ÷ Receita Líquida | Maior |
| **Margem EBIT** | EBIT ÷ Receita Líquida | Maior |
| **Margem Líquida** | Lucro Líquido ÷ Receita Líquida | Maior |
| **ROA** | Lucro Líquido ÷ Ativo Total | Maior |
| **ROE** | Lucro Líquido ÷ Patrimônio Líquido | Maior |
            """)

            st.markdown("#### Liquidez")
            st.markdown("""
| Indicador | Fórmula | Referência |
|---|---|---|
| **Liq. Corrente** | AC ÷ PC | > 1,0 |
| **Liq. Seca** | (AC − Estoques) ÷ PC | > 0,8 |
| **Liq. Imediata** | Caixa ÷ PC | > 0,2 |
| **Liq. Geral** | (AC + RLP) ÷ (PC + PNC) | > 1,0 |
            """)

            st.markdown("#### Endividamento")
            st.markdown("""
| Indicador | Fórmula | Bom quando |
|---|---|---|
| **Endividamento Geral** | Passivo Total ÷ Ativo Total | Menor |
| **Grau de Endividamento** | Passivo Total ÷ PL | Menor |
| **Comp. Endividamento** | PC ÷ Passivo Total | Menor (curto prazo) |
            """)

        with col_l:
            st.markdown("#### Ciclos Operacionais")
            st.markdown("""
| Indicador | Fórmula | Bom quando |
|---|---|---|
| **PMRV** | Recebíveis ÷ (Receita ÷ 365) | Menor |
| **PME** | Estoques ÷ (CPV ÷ 365) | Menor |
| **PMPF** | Fornecedores ÷ (CPV ÷ 365) | Maior |
| **Ciclo Operacional** | PMRV + PME | Menor |
| **Ciclo Financeiro** | Ciclo Op. − PMPF | Menor (negativo = ótimo) |
            """)

            st.markdown("#### Capital de Giro")
            st.markdown("""
| Indicador | Fórmula | Interpretação |
|---|---|---|
| **NCG** | AC Operacional − PC Operacional | Necessidade de capital |
| **CGL** | AC − PC | Capital de giro líquido |
| **CGP** | PL + PNC − ANC | Capital de giro próprio |
| **ST (Saldo Tesouraria)** | CGL − NCG | Folga financeira |
            """)

            st.markdown("---")
            st.info("""
**Sobre o Z-Score no Heatmap**

No heatmap de setores, cada indicador é normalizado como:

$$z = \\frac{x - \\mu}{\\sigma}$$

Para indicadores onde **menor é melhor** (ciclos, endividamento), o z-score é **negado**,
garantindo que valores melhores sempre apareçam em verde.
            """)

    # ─────────────────────────────────────────────────────────────────────────
    # IA ANALYST
    # ─────────────────────────────────────────────────────────────────────────
    with tab_ia:
        st.subheader("IA Analyst — Como Funciona")
        st.markdown(
            "O módulo de IA está em `ai_analyst.py` e é composto por três camadas independentes: "
            "**construção de contexto**, **montagem do prompt** e **chamada ao modelo**."
        )
        st.markdown("---")

        # ── Etapa 1: Contexto ────────────────────────────────────────────────
        st.markdown("### Etapa 1 — Construção do Contexto")
        st.markdown("""
Cada tela tem uma função `build_context_*()` que lê os dados tabulares do banco e os converte
em **texto estruturado** antes de enviar ao modelo. Isso é fundamental: LLMs entendem melhor
contexto em linguagem natural do que JSON ou DataFrames brutos.

**Exemplo — contexto gerado pela tela de Indicadores (`build_context_indicadores`):**
        """)
        st.code("""
EMPRESA: PETRÓLEO BRASILEIRO S.A. - PETROBRAS
PERÍODOS ANALISADOS: 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31
ÚLTIMO PERÍODO: 2024-12-31

=== RENTABILIDADE (último período) ===
  Margem Líquida:  24.3%
  Margem Bruta:    51.8%
  Margem EBIT:     35.1%
  ROE:             31.2%
  ROA:             12.4%

=== LIQUIDEZ (último período) ===
  Liq. Corrente:   1.08
  Liq. Seca:       0.94
  Liq. Imediata:   0.41
  Endividamento:   62.1%

=== CICLOS OPERACIONAIS (último período) ===
  PMRV:            18 dias
  PME:             42 dias
  PMPF:            67 dias
  Ciclo Financ.:   -7 dias

=== EVOLUÇÃO DA MARGEM LÍQUIDA (série histórica) ===
  2021-12-31: 18.7%
  2022-12-31: 30.5%
  2023-12-31: 26.1%
  2024-12-31: 24.3%

SETOR: Petróleo, Gás e Biocombustíveis
        """, language="text")

        st.markdown("""
**Funções disponíveis por tela:**

| Função | Tela | O que inclui no contexto |
|---|---|---|
| `build_context_indicadores()` | Indicadores | Todos os KPIs + série histórica da Margem Líquida + setor |
| `build_context_bp()` | Balanço Patrimonial | Ativo, Passivo, PL em R$ MM + CAGR + variação YoY |
| `build_context_dre()` | DRE | Receita, margens, EBIT, lucro + variações percentuais |
| `build_context_dfc()` | DFC | FCO, FCI, FCF + FCF acumulado + qualidade do caixa |
| `build_context_comparativo_empresas()` | Emp × Emp | Tabela lado a lado: 7 KPIs de cada empresa |
| `build_context_vs_setor()` | Emp × Setor | Empresa vs mediana do setor + diferença % por indicador |
| `build_context_vs_todos_setores()` | Emp × Setores | Posição da empresa em cada indicador vs todos os setores |
        """)

        st.markdown("---")

        # ── Etapa 2: System Prompt ───────────────────────────────────────────
        st.markdown("### Etapa 2 — System Prompt e Persona")
        st.markdown("""
Antes do contexto dos dados, o modelo recebe um **system prompt** que define sua persona e regras
de comportamento. Isso garante consistência nas respostas independentemente da empresa ou tela:
        """)
        st.code("""
Você é um analista financeiro sênior especializado em empresas de capital aberto
brasileiras listadas na CVM (Comissão de Valores Mobiliários).

Suas análises devem:
- Ser objetivas, diretas e baseadas estritamente nos dados fornecidos.
- Destacar pontos positivos e negativos de forma equilibrada.
- Usar linguagem acessível mas profissional, em português do Brasil.
- Evitar especulações que vão além dos dados apresentados.
- Estruturar a resposta com seções curtas e bullet points quando útil.
- Não inventar dados ou citar valores que não foram fornecidos.
        """, language="text")

        st.markdown("---")

        # ── Etapa 3: User Prompt ─────────────────────────────────────────────
        st.markdown("### Etapa 3 — Prompt Específico por Tela")
        st.markdown("""
Além do system prompt, cada tela tem sua própria função `_prompt_*()` que monta o **user prompt**:
o contexto dos dados + as perguntas específicas que o modelo deve responder.
        """)

        ex1, ex2 = st.tabs(["Prompt — Indicadores", "Prompt — Empresa vs Setor"])

        with ex1:
            st.code("""
Analise os indicadores financeiros abaixo da empresa PETROBRAS.

[... contexto com todos os KPIs ...]

Por favor, forneça:
1. **Saúde Financeira Geral** — avaliação rápida do estado atual da empresa.
2. **Pontos Fortes** — o que se destaca positivamente nos dados.
3. **Pontos de Atenção** — riscos ou fraquezas identificados.
4. **Tendência Histórica** — o que a evolução da Margem Líquida sugere.
5. **Conclusão** — uma frase objetiva resumindo o posicionamento financeiro.

Seja conciso. Use bullet points nas seções 2, 3 e 4.
            """, language="text")

        with ex2:
            st.code("""
Analise o comparativo financeiro abaixo (Empresa vs Setor (Petróleo, Gás e Biocombustíveis)).

EMPRESA vs SETOR — PERÍODO: 2024-12-31
Empresa: PETROBRAS | Setor benchmark: Petróleo, Gás e Biocombustíveis

INDICADOR              EMPRESA   MEDIANA SETOR   DIFERENÇA
-----------------------------------------------------------------
  Margem Líquida         24.3%          18.1%       +34.3%
  ROE                    31.2%          14.7%      +112.2%
  Liq. Corrente           1.08           1.21        -10.7%
  Endividamento          62.1%          55.4%        +12.1%
  Ciclo Financ.          -7 dias        12 dias     -158.3%

Por favor, forneça:
1. **Destaques** — qual empresa/setor se sobressai e por quê.
2. **Pontos de Divergência** — onde há maiores diferenças e o que isso indica.
3. **Análise de Risco** — perfil de risco comparativo.
4. **Recomendação de Foco** — onde um analista deveria aprofundar a investigação.

Seja conciso e direto. Use bullet points.
            """, language="text")

        st.markdown("---")

        # ── Etapa 4: Chamada à API ───────────────────────────────────────────
        st.markdown("### Etapa 4 — Chamada ao Modelo (Groq + LLaMA)")
        col_a, col_b = st.columns([2, 1], gap="large")

        with col_a:
            st.markdown("""
A função `_call_groq()` centraliza toda a comunicação com a API:

```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ],
    max_tokens=1200,
    temperature=0.3,
)
```

**Por que esses parâmetros?**
- **Temperature 0.3** — respostas mais determinísticas e factuais. Temperaturas altas
  tornam o modelo mais "criativo", o que não é desejável em análise financeira.
- **Max tokens 1200** — suficiente para uma análise completa com 4–5 seções sem
  truncar a resposta nem consumir tokens desnecessários.
- **LLaMA 3.3 70B Versatile** — 70 bilhões de parâmetros. Um dos maiores modelos
  open-source disponíveis, com forte desempenho em raciocínio analítico.
- **Groq** — hardware especializado (LPU) que executa o modelo com latência de
  1–3 segundos, viável para uso em tempo real no dashboard.
            """)

        with col_b:
            st.markdown("""
**Modelo escolhido:**

`llama-3.3-70b-versatile`

| Atributo | Valor |
|---|---|
| Parâmetros | 70 bilhões |
| Tipo | Open-source (Meta) |
| Inferência | Groq LPU |
| Latência típica | 1–3 segundos |
| Custo | Gratuito (tier free Groq) |
| Idioma | Multilingual |

---

**Configuração:**

A `GROQ_API_KEY` é lida do
arquivo `.env` via `python-dotenv`.
Nunca é exposta no código-fonte.
            """)

        st.markdown("---")

        # ── Lazy loading ─────────────────────────────────────────────────────
        st.markdown("### Lazy Initialization — por que importa")
        st.markdown("""
O cliente Groq **não é criado na inicialização do app**. Ele só é instanciado quando o usuário
clica no botão "Gerar Análise" dentro de cada tela:

```python
def _get_groq_client():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return None, "GROQ_API_KEY não configurada no arquivo .env."
    from groq import Groq          # import também é lazy
    return Groq(api_key=api_key), None
```

**Benefícios:**
- O dashboard funciona normalmente mesmo sem a API key configurada
- Nenhuma latência de rede na inicialização ou navegação entre telas
- O pacote `groq` só é importado quando realmente necessário
- Erros de configuração são exibidos de forma amigável ao usuário, não como crash
        """)

        st.markdown("---")

        # ── render_ai_panel ──────────────────────────────────────────────────
        st.markdown("### `render_ai_panel()` — Componente de UI")
        st.markdown("""
A função `render_ai_panel()` é o componente visual reutilizado em todas as telas.
Ela recebe o contexto já montado e a função de prompt, e cuida de toda a interação com o usuário:

1. Exibe um **expander** com título e ícone de IA
2. Mostra um **botão** "Gerar Análise"
3. Ao clicar: chama `build_context_*()` → `_prompt_*()` → `_call_groq()` com um spinner
4. Armazena o resultado no `st.session_state` com uma `panel_key` única por tela
5. Re-exibe a última análise gerada até que o usuário clique novamente

Isso garante que a análise **não some ao navegar** entre abas ou filtros — ela fica salva
na sessão até o usuário explicitamente gerar uma nova.
        """)


    # ─────────────────────────────────────────────────────────────────────────
    # DECISÕES TÉCNICAS
    # ─────────────────────────────────────────────────────────────────────────
    with tab_tecnico:
        st.subheader("Decisões Técnicas Interessantes")

        with st.expander("Sistema de Tema Centralizado (`chart_theme.py`)"):
            st.markdown("""
Todos os gráficos do dashboard importam de um único arquivo de tema — `chart_theme.py`.

**O que ele centraliza:**
- `PALETA` — 8 cores pastel da família azul, usadas em ordem por série
- `CORES` — mapeamento semântico (ex: `CORES["verde"]`, `CORES["vermelho"]`)
- Constantes de layout: `GRID_COLOR`, `ZERO_LINE_COLOR`, `HOVER_BG`, `LEGEND_BG`
- Funções `apply_theme()`, `apply_polar_theme()`, `apply_heatmap_theme()`
- Construtores reutilizáveis: `bar_trace()`, `line_trace()`, `area_trace()`, `scatter_polar_trace()`

**Benefício:** mudar qualquer cor ou layout reflete em todos os gráficos de uma vez.
            """)

        with st.expander("Cache Inteligente por TTL (`database.py`)"):
            st.markdown("""
Queries ao PostgreSQL são cacheadas com `@st.cache_data(ttl=...)`:

| TTL | Queries | Motivo |
|---|---|---|
| **3600s (1h)** | Listas de empresas, setores | Raramente mudam |
| **300s (5min)** | Séries históricas, benchmarks | Dados estáveis mas podem ser atualizados |
| **60s (1min)** | Queries pesadas com filtros | Balanço filtrado, demonstrativos |

Isso garante navegação fluida sem hits desnecessários ao banco.
            """)

        with st.expander("Z-Score com Inversão por Semântica (`comparativo.py`)"):
            st.markdown("""
No heatmap de setores, o z-score é calculado coluna a coluna. Porém, para indicadores
onde **um valor menor é melhor** (endividamento, ciclos), o z-score é negado:

```python
z = ((col_data - mn) / sd).fillna(0)
if not TODOS_INDICADORES[col][2]:  # [2] = maior_melhor
    z = -z
```

Isso garante que:
- Uma empresa com **Ciclo Financeiro muito negativo** aparece em **verde**
- Um **Endividamento Geral alto** (ruim) aparece em **vermelho**

A semântica dos indicadores está codificada diretamente em `TODOS_INDICADORES` como uma tupla `(label, tipo, maior_melhor)`.
            """)

        with st.expander("Glossário com Tooltips em Todos os Indicadores (`glossary.py`)"):
            st.markdown("""
O arquivo `glossary.py` centraliza 35+ definições financeiras com fórmula, referência e dica de interpretação.

Qualquer `st.metric()` ou título de gráfico pode chamar:

```python
tooltip("MARGEM_LIQUIDA")
# → "Fórmula: Lucro Líquido ÷ Receita Líquida\\nBoas empresas industriais ficam entre 5–15%..."

chart_tooltip("grafico_margens")
# → "Mostra a evolução histórica das 5 principais margens..."
```

Isso garante que o usuário sempre possa entender o que está vendo sem precisar de documentação externa.
            """)

        with st.expander("Responsividade Mobile (`app.py`)"):
            st.markdown("""
O CSS injeta um bloco `@media (max-width: 768px)` que redefine:

- **Colunas:** wrap automático em grade 2×2 para métricas
- **Fontes:** títulos reduzidos para caber na tela
- **Padding:** margens laterais menores
- **Heatmap:** scroll horizontal com `overflow-x: auto`
- **Botões:** largura 100% para facilitar toque
- **Selectbox/Slider:** área de toque mínima de 44px (padrão WCAG)

O aviso "gire o celular" aparece apenas em telas ≤768px via CSS, sem JS.
            """)

        with st.expander("Banda Interquartil P25–P75 (Empresa vs Setor)"):
            st.markdown("""
Além da mediana do setor, o benchmark também inclui os percentis 25 e 75.
Isso cria uma **faixa visual** atrás de cada barra:

```python
fig.add_shape(
    type="rect",
    x0=j - 0.44, x1=j + 0.44,
    y0=p25v * m, y1=p75v * m,
    fillcolor="rgba(255,255,255,0.06)",
    ...
)
```

A faixa mostra onde estão os 50% centrais das empresas do setor, dando contexto
para avaliar se a empresa está na cauda ou no núcleo da distribuição.
            """)

        with st.expander("6Heatmap Dividido em Abas por Grupo"):
            st.markdown("""
O heatmap original com 14 colunas era ilegível no celular. A solução foi dividir
a função `_render_heatmap_setores()` em duas:

1. `_render_heatmap_grupo()` — renderiza um heatmap para qualquer subconjunto de colunas
2. `_render_heatmap_setores()` — itera pelos grupos de `GRUPOS_INDICADORES` e cria abas Streamlit

A aba "Todos" ao final renderiza o heatmap completo (útil no desktop ou na horizontal).
Isso reduz de 14 para 3–5 colunas por aba, tornando legível mesmo em portrait.
            """)

    # ─────────────────────────────────────────────────────────────────────────
    # FLUXOGRAMAS
    # ─────────────────────────────────────────────────────────────────────────
    with tab_fluxo:
        st.subheader("Fluxogramas da Aplicação")
        st.caption("Visualize a arquitetura, o pipeline de dados e o fluxo de uma análise completa.")

        # helpers reutilizáveis para os diagramas HTML
        def _box(label, bg, border, radius="8px", extra=""):
            return (
                f'<div style="background:{bg};border:1.5px solid {border};border-radius:{radius};'
                f'padding:0.45rem 0.9rem;font-size:0.85rem;font-weight:600;'
                f'box-shadow:0 1px 4px rgba(0,0,0,0.07);white-space:nowrap;{extra}">{label}</div>'
            )

        def _pill(label, bg, border):
            return _box(label, bg, border, radius="50px", extra="padding:0.55rem 1.6rem;font-size:0.92rem;")

        def _arrow(down=True):
            sym = "↓" if down else "→"
            return (
                f'<div style="text-align:center;color:#90CAF9;font-size:1.5rem;'
                f'line-height:1;margin:0.3rem 0;">{sym}</div>'
            )

        def _cluster(title, color_border, color_bg, children_html, emoji=""):
            return (
                f'<div style="border:2px dashed {color_border};border-radius:14px;'
                f'padding:0.8rem 1rem;background:{color_bg};margin-bottom:0.1rem;">'
                f'<div style="font-size:0.73rem;font-weight:700;letter-spacing:0.05em;'
                f'text-transform:uppercase;margin-bottom:0.55rem;color:{color_border};">'
                f'{emoji} {title}</div>'
                f'<div style="display:flex;gap:0.55rem;justify-content:center;flex-wrap:wrap;">'
                f'{children_html}</div></div>'
            )

        _WRAP_OPEN = (
            '<div style="overflow-x:auto;padding:0.5rem 0;">'
            '<div style="min-width:320px;max-width:680px;margin:0 auto;'
            'font-family:Inter,system-ui,sans-serif;color:#13293D;">'
        )
        _WRAP_CLOSE = '</div></div>'

        f1, f2, f3 = st.tabs(["Pipeline de Dados", "Módulos do Dashboard", "Fluxo de Análise IA"])

        # ── Diagrama 1: Pipeline Medallion ───────────────────────────────────
        with f1:
            st.markdown("##### Pipeline completo: da CVM ao usuário final")
            bronze_boxes = (
                _box("DFP (anuais)",     "#FFF8E1", "#FFB300") +
                _box("ITR (trimestrais)","#FFF8E1", "#FFB300") +
                _box("CAD / FRE",        "#FFF8E1", "#FFB300")
            )
            silver_boxes = (
                _box("Empresas", "#E3F2FD", "#90CAF9") +
                _box("BP",       "#E3F2FD", "#90CAF9") +
                _box("DRE",      "#E3F2FD", "#90CAF9") +
                _box("DFC",      "#E3F2FD", "#90CAF9")
            )
            gold_boxes = _box("mart_indicadores_financeiros", "#F3E5F5", "#CE93D8")
            dash_boxes = (
                _box("Balanço",     "#E8F5E9", "#81C784") +
                _box("DRE",         "#E8F5E9", "#81C784") +
                _box("DFC",         "#E8F5E9", "#81C784") +
                _box("Indicadores", "#E8F5E9", "#81C784") +
                _box("Comparativo", "#E8F5E9", "#81C784")
            )
            html = (
                _WRAP_OPEN
                + '<div style="display:flex;justify-content:center;margin-bottom:0.4rem;">'
                + _pill("🌐  CVM — Dados Abertos", "#DBEAFE", "#90CAF9")
                + '</div>'
                + _arrow()
                + _cluster("Camada Bronze — Ingestão",    "#FFB300", "rgba(255,193,7,0.07)",  bronze_boxes, "🥉")
                + _arrow()
                + _cluster("Camada Silver — Normalização","#90CAF9", "rgba(144,202,249,0.07)", silver_boxes, "🥈")
                + _arrow()
                + _cluster("Camada Gold — Indicadores",   "#CE93D8", "rgba(206,147,216,0.07)", gold_boxes,   "🥇")
                + _arrow()
                + _cluster("Dashboard Streamlit",         "#81C784", "rgba(129,199,132,0.07)", dash_boxes,   "📊")
                + _arrow()
                + '<div style="display:flex;justify-content:center;">'
                + _pill("👤  Usuário", "#E3F2FD", "#90CAF9")
                + '</div>'
                + _WRAP_CLOSE
            )
            st.markdown(html, unsafe_allow_html=True)

        # ── Diagrama 2: Módulos do Dashboard ─────────────────────────────────
        with f2:
            st.markdown("##### Dependências entre os módulos Python")
            app_box = '<div style="display:flex;justify-content:center;">' + _pill("app.py", "#DBEAFE", "#90CAF9") + '</div>'
            views_boxes = (
                _box("balanco_patrimonial.py",    "#E8F5E9", "#81C784") +
                _box("dre.py",                    "#E8F5E9", "#81C784") +
                _box("dfc.py",                    "#E8F5E9", "#81C784") +
                _box("indicadores_financeiros.py","#E8F5E9", "#81C784") +
                _box("comparativo.py",            "#E8F5E9", "#81C784") +
                _box("sobre.py",                  "#E8F5E9", "#81C784")
            )
            infra_boxes = (
                _box("database.py",    "#F3E5F5", "#CE93D8") +
                _box("chart_theme.py", "#F3E5F5", "#CE93D8") +
                _box("ai_analyst.py",  "#F3E5F5", "#CE93D8") +
                _box("glossary.py",    "#F3E5F5", "#CE93D8") +
                _box("config.py",      "#F3E5F5", "#CE93D8")
            )
            html2 = (
                _WRAP_OPEN
                + app_box
                + _arrow()
                + _cluster("Views — Telas do Dashboard", "#81C784", "rgba(129,199,132,0.07)", views_boxes)
                + _arrow()
                + _cluster("Infraestrutura Compartilhada", "#CE93D8", "rgba(206,147,216,0.07)", infra_boxes)
                + _arrow()
                + '<div style="display:flex;justify-content:center;">'
                + _pill("PostgreSQL (3 camadas)", "#E3F2FD", "#90CAF9")
                + '</div>'
                + _WRAP_CLOSE
            )
            st.markdown(html2, unsafe_allow_html=True)

        # ── Diagrama 3: Fluxo de Análise IA ──────────────────────────────────
        with f3:
            st.markdown("##### Do clique do usuário à análise gerada pela IA")

            def _step(num, label, bg, border, sublabel=""):
                sub = f'<div style="font-size:0.75rem;font-weight:400;margin-top:0.2rem;opacity:0.75;">{sublabel}</div>' if sublabel else ""
                return (
                    f'<div style="display:flex;align-items:center;gap:0.75rem;margin:0 auto;max-width:440px;">'
                    f'<div style="background:{border};color:#fff;border-radius:50%;width:1.6rem;height:1.6rem;'
                    f'display:flex;align-items:center;justify-content:center;font-size:0.78rem;'
                    f'font-weight:700;flex-shrink:0;">{num}</div>'
                    f'<div style="flex:1;background:{bg};border:1.5px solid {border};border-radius:10px;'
                    f'padding:0.55rem 1rem;font-size:0.88rem;font-weight:600;box-shadow:0 1px 4px rgba(0,0,0,0.07);">'
                    f'{label}{sub}</div></div>'
                )

            steps = (
                _step("①", "Usuário seleciona empresa e período", "#DBEAFE", "#90CAF9")
                + _arrow()
                + _step("②", "database.py — query ao PostgreSQL", "#F3E5F5", "#CE93D8", "Gold Layer: mart_indicadores_financeiros")
                + _arrow()
                + _step("③", "build_context_*() — monta contexto", "#E3F2FD", "#90CAF9", "Converte DataFrame em texto estruturado")
                + _arrow()
                + _step("④", "_prompt_*() — monta user prompt", "#E3F2FD", "#90CAF9", "Contexto + perguntas específicas da tela")
                + _arrow()
                + _step("⑤", "Groq API — LLaMA 3.3 70B", "#FFF8E1", "#FFB300", "temp=0.3 · max_tokens=1200 · ~1–3 segundos")
                + _arrow()
                + _step("⑥", "Resposta em português", "#E8F5E9", "#81C784", "Análise estruturada com bullet points")
                + _arrow()
                + _step("⑦", "session_state — persiste a análise", "#EDE7F6", "#9FA8DA", "Não some ao navegar entre abas ou filtros")
                + _arrow()
                + _step("⑧", "render_ai_panel() — exibe no expander", "#E8F5E9", "#81C784", "Reutilizado em todas as 7 telas")
            )
            st.markdown(_WRAP_OPEN + steps + _WRAP_CLOSE, unsafe_allow_html=True)

