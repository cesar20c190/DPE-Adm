import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Consulta de Termos", layout="centered")
st.title("🔍 Consulta de Termos de Declaração")

# Função para obter o caminho absoluto do banco
def get_banco_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "banco_termos.db"))

# Função de consulta com filtros dinâmicos
def consultar_banco(nome="", cpf="", cidade="", data_inicio=None, data_fim=None):
    caminho_banco = get_banco_path()
    conexao = sqlite3.connect(caminho_banco)

    query = "SELECT * FROM termos WHERE 1=1"
    parametros = []

    if nome:
        query += " AND nome LIKE ?"
        parametros.append(f"%{nome}%")
    
    if cpf:
        query += " AND cpf LIKE ?"
        parametros.append(f"%{cpf}%")

    if cidade:
        query += " AND cidade LIKE ?"
        parametros.append(f"%{cidade}%")

    if data_inicio and data_fim:
        query += " AND date(data) BETWEEN ? AND ?"
        parametros.append(data_inicio)
        parametros.append(data_fim)

    try:
        df = pd.read_sql_query(query, conexao, params=parametros)
    except Exception as e:
        st.error(f"Erro ao consultar o banco: {e}")
        df = pd.DataFrame()
    
    conexao.close()
    return df

# --- Interface de filtros ---
st.markdown("### 🔎 Filtros de Busca")

col1, col2 = st.columns(2)
with col1:
    nome_filtro = st.text_input("Nome do assistido")
    cidade_filtro = st.text_input("Cidade")

with col2:
    cpf_filtro = st.text_input("CPF")
    intervalo = st.checkbox("Filtrar por data")

data_ini, data_fim = None, None
if intervalo:
    col3, col4 = st.columns(2)
    with col3:
        data_ini = st.date_input("Data inicial")
    with col4:
        data_fim = st.date_input("Data final")

# Botão de consulta
if st.button("🔍 Consultar"):
    df_resultado = consultar_banco(
        nome=nome_filtro,
        cpf=cpf_filtro,
        cidade=cidade_filtro,
        data_inicio=str(data_ini) if data_ini else None,
        data_fim=str(data_fim) if data_fim else None
    )

    st.markdown(f"**{len(df_resultado)} registro(s) encontrado(s).**")
    st.dataframe(df_resultado, use_container_width=True)
