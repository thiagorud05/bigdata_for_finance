# Roteiro de Apresentação — CVM Data Lake Dashboard
**Disciplina:** Big Data for Finance · FAE Centro Universitário  
**Duração estimada:** 15–20 minutos  
**Público:** Misto (professores + colegas de curso)

---

## SLIDE 1 — Capa

**Título:** CVM Data Lake Explorer  
**Subtítulo:** Pipeline de dados e dashboard analítico para empresas abertas brasileiras  
**Elementos visuais:** logo FAE, print do dashboard, nomes dos autores

**Notas de orador:**
> "Hoje vamos apresentar um projeto que vai da coleta de dados brutos da CVM até um dashboard
> interativo com análise por inteligência artificial. O objetivo é mostrar como Big Data
> pode tornar acessível uma análise financeira que normalmente exigiria horas de trabalho manual."

---

## SLIDE 2 — O Problema

**Título:** Dados financeiros públicos, mas difíceis de usar

**Bullets:**
- A CVM publica demonstrativos de **~700 empresas abertas** (BP, DRE, DFC)
- Chegam como dezenas de **CSVs por ano**, sem padronização entre empresas
- Hierarquia de contas contábeis é heterogênea — mesmo "Caixa" pode estar em códigos diferentes
- Comparar empresas ou setores exige **junções manuais + cálculos repetitivos**
- Analistas gastam horas **só na preparação dos dados**, antes de qualquer insight

**Visual sugerido:** print de arquivo CSV bruto da CVM mostrando as colunas cruas

**Notas de orador:**
> "Quem já tentou baixar os dados da CVM e trabalhar direto neles sabe: é uma bagunça.
> Arquivos separados por ano e tipo, colunas diferentes dependendo do formulário, contas sem
> padronização entre empresas. O problema não é falta de dados — é falta de estrutura."

---

## SLIDE 3 — A Solução

**Título:** Um pipeline completo: da coleta ao insight

**Bullets:**
- **Coleta automática** de dados da CVM via API pública
- **Limpeza e padronização** — hierarquia de contas, validação de equações contábeis
- **Cálculo automático** de 20+ indicadores financeiros
- **Dashboard interativo** com 6 telas analíticas
- **Benchmarks setoriais** — compare com a mediana do setor
- **IA integrada** — análise textual por LLM em cada tela

**Visual sugerido:** diagrama simples com 4 blocos: Coleta → Tratamento → Indicadores → Dashboard

**Notas de orador:**
> "A resposta foi construir um pipeline completo que resolve todos esses problemas de uma vez.
> Não é só um dashboard — é uma infraestrutura de dados que qualquer analista pode usar."

---

## SLIDE 4 — Arquitetura Medallion

**Título:** Medallion Architecture: Bronze → Silver → Gold

**Diagrama (3 colunas):**

| 🥉 Bronze | 🥈 Silver | 🥇 Gold |
|---|---|---|
| Dados brutos CVM | Dados limpos e padronizados | Indicadores calculados |
| CSVs via API | BP, DRE, DFC normalizados | `mart_indicadores_financeiros` |
| `layer_01_bronze` | `layer_02_silver` | `layer_03_gold` |

**Bullets adicionais:**
- Padrão consolidado em engenharia de dados (Delta Lake, Databricks, etc.)
- Cada camada tem qualidade e propósito crescentes
- Processado via **Jupyter Notebooks** → persiste no **PostgreSQL**

**Notas de orador:**
> "A Medallion Architecture é um padrão muito usado em engenharia de dados moderna.
> A ideia é simples: os dados vão ficando mais refinados a cada camada.
> Na Bronze chegam exatamente como a CVM entrega. Na Silver já estão limpos.
> Na Gold já estão prontos para consumo analítico — qualquer query vira gráfico."

---

## SLIDE 5 — Stack Tecnológico

**Título:** Tecnologias utilizadas

**Tabela (duas colunas):**

| Pipeline de dados | Dashboard e IA |
|---|---|
| Python 3.10+ | Streamlit ≥ 1.35 |
| PostgreSQL | Plotly ≥ 5.18 |
| SQLAlchemy 2.0 | Groq API |
| pandas 2.0 | LLaMA 3.3 70B |
| NumPy | python-dotenv |
| Jupyter Notebooks | |

**Notas de orador:**
> "Todo o projeto é Python. Usamos pandas e SQLAlchemy para manipulação e persistência dos dados,
> Streamlit para o frontend — que permite criar dashboards interativos com muito menos código que
> frameworks web tradicionais — e a API da Groq para rodar o LLaMA com baixíssima latência."

---

## SLIDE 6 — Camada Bronze: Coleta

**Título:** Bronze — Coleta automatizada da CVM

**Bullets:**
- Fonte: **dados.cvm.gov.br** (API pública e gratuita)
- Tipos coletados: DFP (anuais), ITR (trimestrais), FRE, CAD (cadastro)
- Download automático por ano e tipo de documento
- Armazenado sem transformações — preserva os dados originais
- Log de coleta para rastreabilidade

**Visual sugerido:** snippet do notebook `2_coletando_dados_fre.ipynb` mostrando o download

**Notas de orador:**
> "A camada Bronze é a nossa fonte da verdade. Não modificamos nada aqui —
> se der algum problema em qualquer etapa, podemos sempre voltar ao dado original."

---

## SLIDE 7 — Camada Silver: Tratamento

**Título:** Silver — Normalização e validação

**Bullets:**
- Seleção das empresas de interesse (tabela `n0_empresas_selecionadas`)
- Padronização da hierarquia de contas (1 → 1.01 → 1.01.01)
- Filtragem: apenas demonstrativos **consolidados** (padrão IFRS)
- Validação contábil: **Ativo = Passivo + PL** (linha de sanidade no dashboard)
- Resultado: 3 tabelas limpas — BP, DRE, DFC

**Visual sugerido:** diagrama de hierarquia de contas CVM

**Notas de orador:**
> "A Silver é onde acontece o trabalho mais difícil. Cada empresa usa estruturas
> ligeiramente diferentes para as mesmas contas. O desafio foi criar regras genéricas
> que funcionassem para qualquer empresa, sem hardcode por empresa.
> No final, temos 6 testes de sanidade que verificam se os dados fazem sentido."

---

## SLIDE 8 — Camada Gold: Indicadores

**Título:** Gold — 20+ indicadores calculados automaticamente

**Grupos:**
- **Rentabilidade (5):** Margem Bruta, EBIT, Líquida, ROA, ROE
- **Liquidez (4):** Corrente, Seca, Imediata, Geral
- **Endividamento (3):** Geral, Grau, Composição
- **Ciclos (5):** PMRV, PME, PMPF, Ciclo Operacional, Ciclo Financeiro
- **Capital de Giro (4):** NCG, CGL, CGP, Saldo Tesouraria

**Fórmula exemplo:**
```
Ciclo Financeiro = Ciclo Operacional − PMPF
                = (PMRV + PME) − PMPF
```

**Notas de orador:**
> "Com os dados padronizados, calcular os indicadores é simples — e o mais importante:
> é automático. Toda vez que chegam dados novos, os indicadores são recalculados.
> Isso significa que qualquer empresa no banco já tem 20 KPIs prontos para análise."

---

## SLIDE 9 — DEMO: Balanço Patrimonial

**Título:** Tela 1 — Balanço Patrimonial

**Bullets (com print do gráfico ao lado):**
- Sunburst interativo — drill-down de Ativo e Passivo + PL
- Composição do ativo ao longo do tempo (stacked area)
- Estrutura de capital — barras divergentes
- Controles: data, nível de detalhe, escala (R$, mil, MM, bilhões)
- Análise da IA: estrutura de capital, riscos, alavancagem

**Notas de orador:**
> "A primeira tela é o Balanço. O sunburst permite que o usuário explore a estrutura do ativo
> e passivo de forma visual, fazendo drill-down nos grupos. Aqui já dá pra ver rapidamente
> se uma empresa tem caixa sólido, se está endividada no curto prazo, e assim por diante."

---

## SLIDE 10 — DEMO: DRE

**Título:** Tela 2 — Demonstração do Resultado

**Bullets (com print do waterfall):**
- Waterfall da Receita ao Lucro Líquido (cascata)
- Evolução histórica das margens (Bruta, EBIT, Líquida, ROA, ROE)
- Decomposição de custos (% da receita): CPV, Despesas, Financeiro, IR
- Funil de margens: quanto de cada R$ de receita vira lucro em cada etapa

**Notas de orador:**
> "O gráfico waterfall é o favorito da turma — ele mostra visualmente como a receita
> vai sendo 'consumida' por custos, despesas e impostos até chegar ao lucro líquido.
> Em um segundo você entende onde a empresa está perdendo margem."

---

## SLIDE 11 — DEMO: DFC

**Título:** Tela 3 — Fluxo de Caixa

**Bullets:**
- FCO (operacional), FCI (investimento), FCF (financiamento) — barras agrupadas
- Mapa FCO × FCI com 4 quadrantes:
  - 🟢 Saudável: opera bem e investe
  - 🔴 Alerta: queima caixa operacional
  - 🔵 Desinvestimento: vende ativos para sobreviver
- Free Cash Flow = FCO + FCI (quanto sobra depois de investir)

**Notas de orador:**
> "O fluxo de caixa é muitas vezes mais revelador que o resultado contábil.
> Uma empresa pode ter lucro no DRE mas queimar caixa. O mapa de quadrantes
> permite identificar isso de forma imediata — empresa no quadrante vermelho,
> atenção máxima."

---

## SLIDE 12 — DEMO: Indicadores Financeiros

**Título:** Tela 4 — Painel de Indicadores

**Bullets (com print dos gauges):**
- Cards por grupo: Rentabilidade, Liquidez, Ciclos
- Gauges (velocímetros) com zonas de cor para os principais KPIs
- Evolução histórica de todos os indicadores em gráficos
- Tabela completa: 22 indicadores + download CSV
- Tooltips em cada card explicando fórmula e referência

**Notas de orador:**
> "Aqui está o painel consolidado de saúde financeira da empresa.
> Os gauges foram pensados para uma leitura rápida — verde, amarelo, vermelho.
> Os tooltips em cada indicador explicam a fórmula e o que é considerado um bom valor,
> sem precisar consultar nenhum livro."

---

## SLIDE 13 — DEMO: Comparativo — Empresa vs Empresa

**Título:** Tela 5A — Empresa vs Empresa

**Bullets:**
- Seleciona 2 a 5 empresas + data de referência
- Radar com 7 KPIs normalizados — visualização simultânea das forças
- Barras agrupadas por grupo de indicadores
- Evolução temporal lado a lado — Margem Líquida
- Tabela com todos os 20 indicadores e coluna de glossário

**Notas de orador:**
> "No Comparativo, o usuário pode colocar concorrentes lado a lado.
> O radar é ótimo para uma visão holística — dá pra ver de um relance
> qual empresa é mais líquida, qual tem melhor margem, qual está mais endividada."

---

## SLIDE 14 — DEMO: Empresa vs Setor

**Título:** Tela 5B — Empresa vs Setor

**Bullets:**
- Setor detectado automaticamente pelo cadastro CVM
- Benchmark = **mediana** das empresas do setor
- Bandas P25–P75 mostram onde estão os 50% centrais do setor
- Scorecard com delta vs mediana (lógica invertida para endividamento)
- Evolução temporal: empresa vs mediana histórica do setor

**Notas de orador:**
> "O benchmark por setor é um dos recursos mais úteis.
> Não basta saber que a margem é 8% — é preciso saber se isso é bom ou ruim no setor.
> As bandas P25–P75 mostram se a empresa está na cauda ou no núcleo da distribuição."

---

## SLIDE 15 — DEMO: Empresa vs Todos os Setores

**Título:** Tela 5C — Empresa vs Todos os Setores

**Bullets:**
- Heatmap Z-Score com **todos os setores**
- Empresa destacada no topo (★) com borda colorida
- Z-Score negado para indicadores onde menor = melhor
- Dividido em abas: Rentabilidade / Liquidez / Endividamento / Ciclos / Todos
- Ranking por indicador: qual setor é melhor em cada KPI

**Visual sugerido:** print do heatmap com a linha da empresa destacada

**Notas de orador:**
> "Esse é o heatmap de posicionamento global.
> O verde significa que aquele setor está acima da média naquele indicador,
> e a empresa aparece no topo para comparação imediata.
> Um detalhe técnico importante: para indicadores como ciclo financeiro,
> onde um valor negativo é ótimo, invertemos o z-score — então negativo = verde."

---

## SLIDE 16 — IA Analyst

**Título:** Inteligência Artificial integrada em cada tela

**Fluxo:**
```
Dados (Gold Layer)
    ↓ Contexto estruturado
Prompt específico por tela
    ↓ API Groq
LLaMA 3.3 70B (70 bilhões de parâmetros)
    ↓
Análise em português
```

**Bullets:**
- Modelo: **LLaMA 3.3 70B** via Groq (inferência ultra-rápida)
- Temperature baixa (0.3) → respostas consistentes e factuais
- 7 contextos diferentes (um por tela/modo)
- Lazy loading — o cliente só inicia quando o usuário clica
- Análise focada: pontos fortes, fracos, riscos, tendências

**Notas de orador:**
> "O LLaMA 3.3 70B é um dos maiores modelos open-source disponíveis.
> A Groq consegue rodar ele com latência de segundos, o que torna viável
> colocar numa aplicação interativa.
> A chave aqui é a construção do contexto — cada tela tem uma função que traduz
> os dados tabulares em linguagem natural antes de enviar pro modelo."

---

## SLIDE 17 — Decisões Técnicas

**Título:** Decisões técnicas que fizeram diferença

**4 bullets principais:**

1. **Cache por TTL** — queries pesadas ficam em cache (60s a 1h), navegação sem travamento

2. **Tema centralizado** — `chart_theme.py` controla cores e layout de todos os ~30 gráficos de um lugar só

3. **Z-Score com inversão semântica** — indicadores "menor é melhor" têm z-score negado automaticamente no heatmap

4. **Heatmap em abas** — de 14 colunas ilegíveis no mobile para 3–5 colunas por aba (Rentabilidade / Liquidez / Endividamento / Ciclos / Todos)

**Bônus:**
- Glossário de 35+ indicadores com fórmulas acessíveis por tooltip em qualquer card
- CSS responsivo com media queries para mobile (grade 2×2, touch targets 44px)

**Notas de orador:**
> "Algumas decisões parecem pequenas mas fazem muita diferença na experiência.
> O cache foi o que tornou o dashboard navegável — sem ele, cada clique esperaria
> 3–5 segundos de query no banco.
> O heatmap em abas foi uma decisão de UX — o original era ilegível no celular."

---

## SLIDE 18 — Resultados e Próximos Passos

**Título:** O que temos hoje e o que vem a seguir

**O que foi entregue:**
- Pipeline completo Bronze → Silver → Gold
- Dashboard com 6 telas + 3 modos de comparativo
- 20+ indicadores calculados automaticamente
- IA integrada em todas as telas
- Responsivo para mobile
- Documentação dos indicadores (`racional_indicadores/`)

**Próximos passos possíveis:**
- Automatizar atualização periódica dos dados (scheduler)
- Alertas automáticos de deterioração de indicadores
- Adicionar mais empresas / expandir cobertura setorial
- Análise de séries temporais com previsão (Prophet, ARIMA)
- Integrar dados de preço de mercado (P/L, EV/EBITDA)

**Notas de orador:**
> "O projeto está funcional e com dados reais. O que apresentamos aqui é uma
> prova de conceito que já pode ser usada para análise real de empresas CVM.
> Os próximos passos naturais seriam automatizar a atualização e expandir
> para análises preditivas."

---

## SLIDE 19 — Conclusão

**Título:** Big Data transforma dados públicos em inteligência

**Mensagem central:**
> "Dados financeiros da CVM são públicos e gratuitos.  
> A barreira não é acesso — é estrutura.  
> Engenharia de dados bem feita remove essa barreira."

**Takeaways:**
- Medallion Architecture organiza dados progressivamente
- Cache e tema centralizado tornam sistemas escaláveis e mantíveis
- IA não substitui o analista — mas elimina o trabalho repetitivo de leitura de tabelas
- Streamlit + Plotly + PostgreSQL é uma stack poderosa para dashboards analíticos em Python

**Notas de orador:**
> "A conclusão é simples: o problema não era falta de dados, era falta de estrutura.
> Com as ferramentas certas e boas decisões de engenharia, transformamos dados brutos
> que ninguém usa em um dashboard que qualquer analista consegue operar.
> Obrigado — ficamos à disposição para perguntas."

---

## APÊNDICE — Estrutura de Arquivos

```
BigData_For_Finance/
├── notebooks/
│   ├── 01_bronze/          # Coleta CVM
│   ├── 02_silver/          # Limpeza e normalização
│   └── 03_gold/            # Cálculo de indicadores
├── dashboard/
│   ├── app.py              # Entry point, navegação, CSS
│   ├── config.py           # Configurações globais
│   ├── database.py         # Data access layer (22 funções)
│   ├── chart_theme.py      # Tema centralizado de gráficos
│   ├── ai_analyst.py       # IA: contexto + prompts + Groq
│   ├── glossary.py         # Dicionário de 35+ indicadores
│   └── views/
│       ├── balanco_patrimonial.py
│       ├── dre.py
│       ├── dfc.py
│       ├── indicadores_financeiros.py
│       ├── comparativo.py  # 3 modos de comparativo
│       ├── explorer.py     # Explorador de dados brutos
│       ├── monitoring.py   # Monitoramento do data lake
│       └── sobre.py        # Esta apresentação (no dashboard)
└── racional_indicadores/
    ├── indicadores_financeiros.md   # Fórmulas e racional
    └── data_contract_tabela_gold.md # Contrato da tabela Gold
```

---

## APÊNDICE — Indicadores: Maior vs Menor é melhor

| Indicador | Bom quando |
|---|---|
| Margem Bruta / EBIT / Líquida | **Maior** |
| ROA, ROE | **Maior** |
| Liquidez Corrente / Seca / Imediata / Geral | **Maior** |
| Endividamento Geral | **Menor** |
| Grau de Endividamento | **Menor** |
| Composição do Endividamento | **Menor** (menos dívida curto prazo) |
| PMRV (prazo de recebimento) | **Menor** |
| PME (prazo de estoque) | **Menor** |
| PMPF (prazo de pagamento) | **Maior** (paga depois) |
| Ciclo Operacional | **Menor** |
| Ciclo Financeiro | **Menor** (negativo = empresa financia-se com fornecedores) |
