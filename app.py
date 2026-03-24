import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Dashboard - Controle de Presença Board")

# =========================
# LEITURA GOOGLE SHEETS
# =========================
url = "https://docs.google.com/spreadsheets/d/1LWPHqqmLCaqHjCGrLADyR4jPRVK05CxnQQNEheHmAZ4/export?format=csv"

df = pd.read_csv(url)

# =========================
# AJUSTE DA ESTRUTURA
# =========================
df = df.iloc[4:].reset_index(drop=True)

df.columns = df.iloc[0]
df = df[1:].reset_index(drop=True)

# LIMPEZA
df = df.loc[:, df.columns.notna()]
df = df.loc[:, ~df.columns.duplicated()]
df.columns = df.columns.astype(str).str.strip().str.upper()

# =========================
# IDENTIFICAR COLUNAS
# =========================
def find_col(keyword):
    for col in df.columns:
        if keyword in col:
            return col
    return None

col_nome = find_col("NOME")
col_turma = find_col("TURMA")
col_status = find_col("STATUS")

# =========================
# CRIAR BASE PADRÃO
# =========================
df["nome"] = df[col_nome] if col_nome else ""
df["turma"] = df[col_turma] if col_turma else ""
df["status"] = df[col_status] if col_status else ""

# NORMALIZA STATUS
df["status"] = df["status"].astype(str).str.strip().str.lower()

# =========================
# BASE EDITÁVEL
# =========================
st.subheader("Base de Dados")
df = st.data_editor(df, num_rows="dynamic")

# =========================
# TRATAMENTO TURMA / EDIÇÃO
# =========================
df["turma"] = df["turma"].astype(str).str.strip()

split_cols = df["turma"].str.split(" - ", n=1, expand=True)

if split_cols.shape[1] == 2:
    df["turma_nome"] = split_cols[0]
    df["edicao"] = split_cols[1]
else:
    df["turma_nome"] = df["turma"]
    df["edicao"] = "Não identificado"

# =========================
# CLASSIFICAÇÃO STATUS
# =========================
df["reposicao"] = df["status"].str.contains("repos")
df["ausente"] = df["status"].str.contains("ausente")
df["confirmado"] = df["status"].str.contains("confirmado")

# =========================
# KPIs GERAIS
# =========================
st.markdown("## 📊 Visão Geral")

col1, col2, col3, col4 = st.columns(4)

total = len(df)
repos = df["reposicao"].sum()
ausentes = df["ausente"].sum()
confirmados = df["confirmado"].sum()

taxa_repos = (repos / total * 100) if total > 0 else 0

col1.metric("Participantes", total)
col2.metric("Reposições", repos)
col3.metric("Ausentes", ausentes)
col4.metric("Confirmados", confirmados)

st.metric("Taxa de Reposição", f"{taxa_repos:.1f}%")

st.divider()

# =========================
# ANÁLISES
# =========================
st.markdown("## 📈 Análises")

st.subheader("Participantes por Turma")
st.bar_chart(df.groupby("turma_nome")["nome"].count())

st.divider()

st.subheader("Reposições por Turma")
st.bar_chart(df[df["reposicao"]].groupby("turma_nome")["nome"].count())

st.divider()

st.subheader("Status por Turma")
status_por_turma = df.groupby(["turma_nome", "status"]).size().unstack(fill_value=0)
st.bar_chart(status_por_turma)

st.divider()

# =========================
# FILTROS
# =========================
st.sidebar.title("Filtros")

lista_edicoes = sorted(df["edicao"].dropna().unique())
edicao = st.sidebar.selectbox("Selecione a edição", lista_edicoes)

df_edicao = df[df["edicao"] == edicao]

lista_turmas = sorted(df_edicao["turma_nome"].dropna().unique())
turma = st.sidebar.selectbox("Selecione a turma", lista_turmas)

df_turma = df_edicao[df_edicao["turma_nome"] == turma]

# =========================
# KPIs DA TURMA
# =========================
st.markdown(f"## 📌 Resumo: {edicao} | {turma}")

col1, col2, col3, col4 = st.columns(4)

total_turma = len(df_turma)
repos_turma = df_turma["reposicao"].sum()
ausentes_turma = df_turma["ausente"].sum()
confirmados_turma = df_turma["confirmado"].sum()

taxa_turma = (repos_turma / total_turma * 100) if total_turma > 0 else 0

col1.metric("Participantes", total_turma)
col2.metric("Reposições", repos_turma)
col3.metric("Ausentes", ausentes_turma)
col4.metric("Confirmados", confirmados_turma)

st.metric("Taxa de Reposição", f"{taxa_turma:.1f}%")

st.divider()

# =========================
# LISTAS
# =========================
st.subheader("Lista de Reposições")
lista_repos = df_turma[df_turma["reposicao"]]

if not lista_repos.empty:
    st.dataframe(
        lista_repos[["nome", "turma_nome", "edicao", "status"]],
        use_container_width=True
    )
else:
    st.info("Nenhuma reposição encontrada")

st.subheader("Lista de Ausentes")
lista_ausentes = df_turma[df_turma["ausente"]]

if not lista_ausentes.empty:
    st.dataframe(
        lista_ausentes[["nome", "turma_nome", "edicao", "status"]],
        use_container_width=True
    )
else:
    st.info("Nenhum ausente")