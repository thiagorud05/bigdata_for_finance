# Dicionário de Premissas - Indicadores Financeiros (Schema Gold)

Este arquivo mapeia as contas contábeis da CVM (Silver) para variáveis genéricas (V00, V01...) que serão consumidas pelos algoritmos em Python/Streamlit na camada Gold. A coluna "Completude" indica o percentual de empresas/anos que possuem valor preenchido para a respectiva conta.

## 1. Contas do Balanço Patrimonial (Ativo)
**Origem:** `layer_02_silver.n1_dfp_cia_aberta_bp`

| Variável | Descrição Lógica | Código CVM | Nome da Conta na Base | Completude |
| :--- | :--- | :--- | :--- | :--- |
| **V00** | Ativo Total | `1` | ATIVO TOTAL | **100.00%** 🟢 |
| **V01** | Ativo Circulante | `1.01` | ATIVO CIRCULANTE | **100.00%** 🟢 |
| **V02** | Caixa e Equivalentes de Caixa | `1.01.01` | CAIXA E EQUIVALENTES DE CAIXA | **99.86%** 🟢 |
| **V03** | Aplicações Financeiras (CP) | `1.01.02` | APLICAÇÕES FINANCEIRAS | **63.33%** 🔴 |
| **V04** | Contas a Receber (Clientes CP) | `1.01.03.01` | CLIENTES | **90.14%** 🟡 |
| **V05** | Estoques | `1.01.04` | ESTOQUES | **88.11%** 🟡 |
| **V06** | Ativo Realizável a Longo Prazo | `1.02.01` | ATIVO REALIZÁVEL A LONGO PRAZO | **99.86%** 🟢 |
| **V07** | Ativo Imobilizado | `1.02.03` | IMOBILIZADO | **99.77%** 🟢 |
| **V08** | Ativo Intangível | `1.02.04` | INTANGÍVEL | **97.88%** 🟢 |

## 2. Contas do Balanço Patrimonial (Passivo e PL)
**Origem:** `layer_02_silver.n1_dfp_cia_aberta_bp`

| Variável | Descrição Lógica | Código CVM | Nome da Conta na Base | Completude |
| :--- | :--- | :--- | :--- | :--- |
| **V09** | Passivo Total | `2` | PASSIVO TOTAL | **100.00%** 🟢 |
| **V10** | Passivo Circulante | `2.01` | PASSIVO CIRCULANTE | **100.00%** 🟢 |
| **V11** | Fornecedores (CP) | `2.01.02` | FORNECEDORES | **100.00%** 🟢 |
| **V12** | Empréstimos e Financiamentos (CP) | `2.01.04` | EMPRÉSTIMOS E FINANCIAMENTOS | **94.68%** 🟡 |
| **V13** | Passivo Não Circulante (ELP) | `2.02` | PASSIVO NÃO CIRCULANTE | **99.91%** 🟢 |
| **V14** | Empréstimos e Financiamentos (LP) | `2.02.01` | EMPRÉSTIMOS E FINANCIAMENTOS | **92.57%** 🟡 |
| **V15** | Patrimônio Líquido | `2.03` | PATRIMÔNIO LÍQUIDO CONSOLIDADO | **100.00%** 🟢 |

## 3. Contas da Demonstração do Resultado (DRE)
**Origem:** `layer_02_silver.n1_dfp_cia_aberta_dre`

| Variável | Descrição Lógica | Código CVM | Nome da Conta na Base | Completude |
| :--- | :--- | :--- | :--- | :--- |
| **V16** | Receita Líquida de Vendas | `3.01` | RECEITA DE VENDA DE BENS E/OU SERVIÇOS | **99.64%** 🟢 |
| **V17** | Custo dos Bens/Serviços Vendidos | `3.02` | CUSTO DOS BENS E/OU SERVIÇOS VENDIDOS | **98.69%** 🟢 |
| **V18** | Lucro Bruto | `3.03` | RESULTADO BRUTO | **99.64%** 🟢 |
| **V19** | Despesas Operacionais | `3.04` | DESPESAS/RECEITAS OPERACIONAIS | **99.77%** 🟢 |
| **V20** | EBIT (Resultado Operacional) | `3.05` | RESULTADO ANTES DO RESULTADO FINANCEIRO E DOS TRIBUTOS | **100.00%** 🟢 |
| **V21** | Resultado Financeiro | `3.06` | RESULTADO FINANCEIRO | **100.00%** 🟢 |
| **V22** | EBT (Resultado Antes dos Tributos) | `3.07` | RESULTADO ANTES DOS TRIBUTOS SOBRE O LUCRO | **100.00%** 🟢 |
| **V23** | Lucro Líquido do Período | `3.11` | LUCRO/PREJUÍZO CONSOLIDADO DO PERÍODO | **100.00%** 🟢 |