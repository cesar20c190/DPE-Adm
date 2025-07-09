import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Consulta de Termos", layout="centered")
st.title("🔍 Consulta de Termos de Declaração")

# Caminho para o banco
def get_banco_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "banco_termos.db"))

# Consulta que junta termos com demandas
def consultar_com_demandas(nome="", cpf="", cidade="", data_inicio=None, data_fim=None):
    caminho_banco = get_banco_path()
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    query = """
        SELECT t.id, t.data_termo, t.regional, t.cidade_atendimento, t.nome, t.cpf, t.rua, t.numero,
               t.bairro, t.cidade_assistido, t.telefone, t.data_nascimento, t.sexo, t.grupo_etnico,
               t.renda_individual, t.renda_familiar, t.materia, t.declaracao,
               d.tipo, d.descricao
        FROM termos t
        LEFT JOIN demandas d ON t.id = d.id_termo
        WHERE 1=1
    """
    parametros = []

    if nome:
        query += " AND t.nome LIKE ?"
        parametros.append(f"%{nome}%")
    if cpf:
        query += " AND t.cpf LIKE ?"
        parametros.append(f"%{cpf}%")
    if cidade:
        query += " AND t.cidade_atendimento LIKE ?"
        parametros.append(f"%{cidade}%")
    if data_inicio and data_fim:
        query += " AND date(t.data_termo) BETWEEN ? AND ?"
        parametros.append(data_inicio)
        parametros.append(data_fim)

    try:
        df = pd.read_sql_query(query, conexao, params=parametros)
    except Exception as e:
        st.error(f"Erro na consulta: {e}")
        df = pd.DataFrame()

    conexao.close()
    return df

# --- Interface de Filtro ---
st.markdown("### 🔎 Filtros")

col1, col2 = st.columns(2)
with col1:
    nome = st.text_input("Nome do assistido")
    cidade = st.text_input("Cidade de atendimento")
with col2:
    cpf = st.text_input("CPF")
    filtrar_data = st.checkbox("Filtrar por data")

data_ini, data_fim = None, None
if filtrar_data:
    col3, col4 = st.columns(2)
    with col3:
        data_ini = st.date_input("De:")
    with col4:
        data_fim = st.date_input("Até:")

# --- Consulta ---
if st.button("🔍 Consultar"):
    df = consultar_com_demandas(
        nome=nome,
        cpf=cpf,
        cidade=cidade,
        data_inicio=str(data_ini) if data_ini else None,
        data_fim=str(data_fim) if data_fim else None
    )

    if df.empty:
        st.warning("Nenhum termo encontrado com os filtros aplicados.")
    else:
        total_encontrados = df["id"].nunique()
        st.markdown(f"**{total_encontrados} termo(s) encontrado(s).**")

        # Agrupar por termo
        termos_agrupados = df.groupby("id")

        for termo_id, grupo in termos_agrupados:
            termo = grupo.iloc[0]

            with st.expander(f"🧾 {termo['nome']} — {termo['cidade_atendimento']} — {termo['data_termo']}", expanded=False):
                st.markdown("#### 📋 Dados do Termo")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Nome:** {termo['nome']}")
                    st.write(f"**CPF:** {termo['cpf']}")
                    st.write(f"**Nascimento:** {termo['data_nascimento']}")
                    st.write(f"**Sexo:** {termo['sexo']}")
                    st.write(f"**Grupo étnico:** {termo['grupo_etnico']}")
                with col2:
                    st.write(f"**Telefone:** {termo['telefone']}")
                    st.write(f"**Endereço:** {termo['rua']}, nº {termo['numero']} - {termo['bairro']}, {termo['cidade_assistido']}")
                    st.write(f"**Renda individual:** {termo['renda_individual']}")
                    st.write(f"**Renda familiar:** {termo['renda_familiar']}")

                st.markdown(f"**Matéria:** {termo['materia']}")
                st.markdown(f"**Declaração:** _{termo['declaracao']}_")

                demandas = grupo[["tipo", "descricao"]].dropna()
                if not demandas.empty:
                    st.markdown("#### 💊 Demandas registradas:")
                    for i, row in demandas.iterrows():
                        st.markdown(f"- **{row['tipo']}**: {row['descricao']}")
                else:
                    st.info("Nenhuma demanda registrada.")
