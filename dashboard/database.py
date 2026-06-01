import os
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import streamlit as st


@st.cache_resource
def get_db_connection():
    user = quote_plus(os.getenv('DB_USER', 'postgres'))
    password = quote_plus(os.getenv('DB_PASS', 'password'))
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    dbname = os.getenv('DB_NAME', 'data_lake')
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}")


@st.cache_data(ttl=3600)
def get_companies_bp():
    engine = get_db_connection()
    query = """
    SELECT DISTINCT "CNPJ_CIA", "DENOM_CIA"
    FROM layer_02_silver.n1_dfp_cia_aberta_bp
    ORDER BY "DENOM_CIA";
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
            df['LABEL_DROPDOWN'] = df['DENOM_CIA'] + ' (' + df['CNPJ_CIA'] + ')'
            return df
    except Exception as e:
        st.error(f"Erro ao listar empresas: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_dates_bp(cnpj):
    engine = get_db_connection()
    query = f"""
    SELECT DISTINCT "DT_REFER"
    FROM layer_02_silver.n1_dfp_cia_aberta_bp
    WHERE "CNPJ_CIA" = '{cnpj}'
    ORDER BY "DT_REFER" DESC;
    """
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=60)
def get_bp_data_filtered(cnpj, dates, max_level):
    engine = get_db_connection()

    # nível 1→1 dígito, 2→3 dígitos (ex: 1.01), 3→5, e assim por diante
    max_digits = (max_level * 2) - 1
    dates_str = "', '".join([str(d) for d in dates])

    query = f"""
    SELECT
        "CD_CONTA",
        "DS_CONTA",
        "DT_REFER",
        "VL_CONTA_TRATADO"
    FROM layer_02_silver.n1_dfp_cia_aberta_bp
    WHERE "CNPJ_CIA" = '{cnpj}'
      AND "DT_REFER" IN ('{dates_str}')
      AND LENGTH(REPLACE("CD_CONTA", '.', '')) <= {max_digits}
    ORDER BY "CD_CONTA", "DT_REFER";
    """
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except Exception as e:
        st.error(f"Erro ao buscar dados do balanço: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_companies_indicadores():
    engine = get_db_connection()
    query = """
    SELECT DISTINCT "CNPJ_CIA", "RAZAO_SOCIAL"
    FROM layer_03_gold.mart_indicadores_financeiros
    WHERE "CNPJ_CIA" IS NOT NULL
    ORDER BY "RAZAO_SOCIAL";
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
            df["LABEL"] = df["RAZAO_SOCIAL"] + " (" + df["CNPJ_CIA"] + ")"
            return df
    except Exception as e:
        st.error(f"Erro ao listar empresas (indicadores): {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_indicadores_data(cnpj):
    engine = get_db_connection()
    query = f"""
    SELECT *
    FROM layer_03_gold.mart_indicadores_financeiros
    WHERE "CNPJ_CIA" = '{cnpj}'
    ORDER BY "DT_REFER" ASC;
    """
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except Exception as e:
        st.error(f"Erro ao buscar indicadores: {e}")
        return pd.DataFrame()


_COLS_INDICADORES = [
    "MARGEM_BRUTA", "MARGEM_EBIT", "MARGEM_LIQUIDA",
    "ROA", "ROE",
    "LIQUIDEZ_CORRENTE", "LIQUIDEZ_SECA", "LIQUIDEZ_IMEDIATA", "LIQUIDEZ_GERAL",
    "ENDIVIDAMENTO_GERAL", "GRAU_ENDIVIDAMENTO", "COMPOSICAO_ENDIVIDAMENTO",
    "PMRV", "PME", "PMPF", "CICLO_OPERACIONAL", "CICLO_FINANCEIRO",
]


@st.cache_data(ttl=3600)
def get_sectors_list():
    engine = get_db_connection()
    query = """
    SELECT DISTINCT "SETOR_ATIV"
    FROM layer_02_silver.n0_empresas_selecionadas
    WHERE "SETOR_ATIV" IS NOT NULL
      AND TRIM("SETOR_ATIV") <> ''
    ORDER BY "SETOR_ATIV";
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
            return df["SETOR_ATIV"].dropna().tolist()
    except Exception as e:
        st.error(f"Erro ao listar setores: {e}")
        return []


@st.cache_data(ttl=300)
def get_sector_benchmark(setor: str, dt_refer: str, incluir_quartis: bool = False):
    """Mediana (e opcionalmente P25/P75) dos indicadores para um setor e data."""
    engine = get_db_connection()

    agg_parts = []
    for col in _COLS_INDICADORES:
        agg_parts.append(f'PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY m."{col}") AS "{col}"')
        if incluir_quartis:
            agg_parts.append(f'PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY m."{col}") AS "{col}_P25"')
            agg_parts.append(f'PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY m."{col}") AS "{col}_P75"')

    agg_sql = ",\n    ".join(agg_parts)

    query = f"""
    SELECT
        {agg_sql}
    FROM layer_03_gold.mart_indicadores_financeiros m
    INNER JOIN layer_02_silver.n0_empresas_selecionadas e
        ON m."CNPJ_CIA" = e."CNPJ_CIA"
    WHERE e."SETOR_ATIV" = '{setor}'
      AND m."DT_REFER" = '{dt_refer}';
    """
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except Exception as e:
        st.error(f"Erro ao buscar benchmark do setor '{setor}': {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_all_sectors_benchmark(dt_refer: str):
    """Mediana de cada indicador por setor para uma data — uma linha por setor."""
    engine = get_db_connection()

    agg_parts = [
        f'PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY m."{col}") AS "{col}"'
        for col in _COLS_INDICADORES
    ]
    agg_sql = ",\n    ".join(agg_parts)

    query = f"""
    SELECT
        e."SETOR_ATIV" AS "SETOR",
        {agg_sql}
    FROM layer_03_gold.mart_indicadores_financeiros m
    INNER JOIN layer_02_silver.n0_empresas_selecionadas e
        ON m."CNPJ_CIA" = e."CNPJ_CIA"
    WHERE m."DT_REFER" = '{dt_refer}'
      AND e."SETOR_ATIV" IS NOT NULL
      AND TRIM(e."SETOR_ATIV") <> ''
    GROUP BY e."SETOR_ATIV"
    ORDER BY e."SETOR_ATIV";
    """
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except Exception as e:
        st.error(f"Erro ao buscar benchmark geral de setores: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_sector_time_series(setor: str):
    """Série temporal da mediana dos indicadores para um setor — uma linha por data."""
    engine = get_db_connection()

    agg_parts = [
        f'PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY m."{col}") AS "{col}"'
        for col in _COLS_INDICADORES
    ]
    agg_sql = ",\n    ".join(agg_parts)

    query = f"""
    SELECT
        m."DT_REFER",
        {agg_sql}
    FROM layer_03_gold.mart_indicadores_financeiros m
    INNER JOIN layer_02_silver.n0_empresas_selecionadas e
        ON m."CNPJ_CIA" = e."CNPJ_CIA"
    WHERE e."SETOR_ATIV" = '{setor}'
      AND m."DT_REFER" IS NOT NULL
    GROUP BY m."DT_REFER"
    ORDER BY m."DT_REFER";
    """
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except Exception as e:
        st.error(f"Erro ao buscar série temporal do setor '{setor}': {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_companies_with_sector():
    engine = get_db_connection()
    query = """
    SELECT DISTINCT
        m."CNPJ_CIA",
        m."RAZAO_SOCIAL",
        COALESCE(e."SETOR_ATIV", m."SETOR") AS "SETOR_ATIV",
        m."TP_MERC"
    FROM layer_03_gold.mart_indicadores_financeiros m
    LEFT JOIN layer_02_silver.n0_empresas_selecionadas e
        ON m."CNPJ_CIA" = e."CNPJ_CIA"
    WHERE m."CNPJ_CIA" IS NOT NULL
    ORDER BY m."RAZAO_SOCIAL";
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
            df["LABEL"] = df["RAZAO_SOCIAL"] + " (" + df["CNPJ_CIA"] + ")"
            return df
    except Exception as e:
        st.error(f"Erro ao listar empresas com setor: {e}")
        return pd.DataFrame()


# dfc_mi e dfc_md apontam para a mesma tabela — o banco não os separa
TABELAS_DFP = {
    "dre":    "layer_02_silver.n1_dfp_cia_aberta_dre",
    "dfc":    "layer_02_silver.n1_dfp_cia_aberta_dfc",
    "dfc_mi": "layer_02_silver.n1_dfp_cia_aberta_dfc",
    "dfc_md": "layer_02_silver.n1_dfp_cia_aberta_dfc",
    "bp":     "layer_02_silver.n1_dfp_cia_aberta_bp",
}


@st.cache_data(ttl=3600)
def get_companies_demonstrativo(tabela_alias: str):
    tabela = TABELAS_DFP.get(tabela_alias)
    if not tabela:
        return pd.DataFrame()
    engine = get_db_connection()
    query = f"""
    SELECT DISTINCT "CNPJ_CIA", "DENOM_CIA"
    FROM {tabela}
    ORDER BY "DENOM_CIA";
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
            df["LABEL_DROPDOWN"] = df["DENOM_CIA"] + " (" + df["CNPJ_CIA"] + ")"
            return df
    except Exception as e:
        st.error(f"Erro ao listar empresas ({tabela_alias}): {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_dates_demonstrativo(cnpj: str, tabela_alias: str):
    tabela = TABELAS_DFP.get(tabela_alias)
    if not tabela:
        return pd.DataFrame()
    engine = get_db_connection()
    query = f"""
    SELECT DISTINCT "DT_REFER"
    FROM {tabela}
    WHERE "CNPJ_CIA" = '{cnpj}'
    ORDER BY "DT_REFER" DESC;
    """
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=60)
def get_demonstrativo_filtered(cnpj: str, dates: tuple, max_level: int,
                               tabela_alias: str):
    tabela = TABELAS_DFP.get(tabela_alias)
    if not tabela:
        return pd.DataFrame()
    engine = get_db_connection()

    max_digits = (max_level * 2) - 1
    dates_str  = "', '".join([str(d) for d in dates])

    query = f"""
    SELECT
        "CD_CONTA",
        "DS_CONTA",
        "DT_REFER",
        "VL_CONTA_TRATADO"
    FROM {tabela}
    WHERE "CNPJ_CIA" = '{cnpj}'
      AND "DT_REFER" IN ('{dates_str}')
      AND LENGTH(REPLACE("CD_CONTA", '.', '')) <= {max_digits}
    ORDER BY "CD_CONTA", "DT_REFER";
    """
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except Exception as e:
        st.error(f"Erro ao buscar demonstrativo ({tabela_alias}): {e}")
        return pd.DataFrame()