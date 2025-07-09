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

                # Lista de demandas com botões individuais de exclusão
                demandas = grupo[["tipo", "descricao"]].dropna()
                if not demandas.empty:
                    st.markdown("#### 💊 Demandas registradas:")
                    for i, row in demandas.iterrows():
                        col_d1, col_d2 = st.columns([5, 1])
                        with col_d1:
                            st.markdown(f"- **{row['tipo']}**: {row['descricao']}")
                        with col_d2:
                            if st.button("🗑️", key=f"excluir_demanda_{termo_id}_{i}"):
                                con = sqlite3.connect(get_banco_path())
                                cur = con.cursor()
                                cur.execute("""
                                    DELETE FROM demandas
                                    WHERE id_termo = ? AND tipo = ? AND descricao = ?
                                """, (termo_id, row["tipo"], row["descricao"]))
                                con.commit()
                                con.close()
                                st.success("Demanda excluída com sucesso.")
                                st.experimental_rerun()
                else:
                    st.info("Nenhuma demanda registrada.")

                st.markdown("---")
                colb1, colb2 = st.columns(2)
                with colb1:
                    if st.button(f"📝 Editar termo #{termo_id}", key=f"editar_{termo_id}"):
                        st.session_state["modo_edicao"] = True
                        st.session_state["id_editar"] = termo_id
                with colb2:
                    if st.button(f"🗑️ Excluir termo #{termo_id}", key=f"excluir_termo_{termo_id}"):
                        st.session_state["confirmar_exclusao"] = termo_id

# --- Formulário de edição (fora do loop) ---
if st.session_state.get("modo_edicao"):
    termo_id = st.session_state["id_editar"]
    st.markdown("---")
    st.subheader(f"✏️ Editar Termo #{termo_id}")

    caminho = get_banco_path()
    con = sqlite3.connect(caminho)
    df_termo = pd.read_sql_query("SELECT * FROM termos WHERE id = ?", con, params=[termo_id])
    con.close()

    if df_termo.empty:
        st.error("❌ Termo não encontrado.")
    else:
        termo = df_termo.iloc[0]
        with st.form(key="form_edicao"):
            nome = st.text_input("Nome", value=termo["nome"])
            cpf = st.text_input("CPF", value=termo["cpf"])
            cidade = st.text_input("Cidade atendimento", value=termo["cidade_atendimento"])
            telefone = st.text_input("Telefone", value=termo["telefone"])
            materia = st.text_input("Matéria", value=termo["materia"])
            declaracao = st.text_area("Declaração", value=termo["declaracao"])
            salvar = st.form_submit_button("💾 Salvar alterações")
            if salvar:
                con = sqlite3.connect(caminho)
                cur = con.cursor()
                cur.execute("""
                    UPDATE termos
                    SET nome = ?, cpf = ?, cidade_atendimento = ?, telefone = ?, materia = ?, declaracao = ?
                    WHERE id = ?
                """, (nome, cpf, cidade, telefone, materia, declaracao, termo_id))
                con.commit()
                con.close()
                st.success("✅ Termo atualizado com sucesso.")
                del st.session_state["modo_edicao"]
                del st.session_state["id_editar"]
                st.experimental_rerun()

# --- Confirmação de exclusão ---
if st.session_state.get("confirmar_exclusao"):
    id_excluir = st.session_state["confirmar_exclusao"]
    st.warning(f"⚠️ Tem certeza que deseja excluir o termo #{id_excluir} (incluindo todas as demandas)?")
    colc1, colc2 = st.columns(2)
    with colc1:
        if st.button("✅ Confirmar exclusão"):
            con = sqlite3.connect(get_banco_path())
            cur = con.cursor()
            cur.execute("DELETE FROM demandas WHERE id_termo = ?", [id_excluir])
            cur.execute("DELETE FROM termos WHERE id = ?", [id_excluir])
            con.commit()
            con.close()
            st.success("✅ Termo e demandas excluídos com sucesso.")
            del st.session_state["confirmar_exclusao"]
            st.experimental_rerun()
    with colc2:
        if st.button("❌ Cancelar"):
            del st.session_state["confirmar_exclusao"]
            st.info("Exclusão cancelada.")
