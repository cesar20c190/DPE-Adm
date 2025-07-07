import streamlit as st
from datetime import date

st.title("Formulário - Ofício Estado (SESAB)")

# Dados principais
data_oficio = st.date_input("Data do ofício", value=date.today())
numero_oficio = st.text_input("Número do ofício (Ex: XXX/2024)")
numero_triagem = st.text_input("Número da triagem")
nome_assistido = st.text_input("Nome do assistido")
nacionalidade = st.text_input("Nacionalidade")
estado_civil = st.text_input("Estado civil")
profissao = st.text_input("Profissão")
rg = st.text_input("RG")
cpf = st.text_input("CPF")
nome_pai = st.text_input("Nome do pai")
nome_mae = st.text_input("Nome da mãe")
endereco = st.text_area("Endereço completo")
telefones = st.text_area("Telefones de contato")
email = st.text_input("Email")
procedimento = st.text_input("Tipo de procedimento necessário")
prazo = st.text_input("Prazo para resposta (Ex: 10 (dez))")

# Gerar texto do ofício
if st.button("Gerar Ofício"):
    st.markdown("---")
    st.markdown(f"""
**Salvador, Bahia, {data_oficio.strftime('%d/%m/%Y')}**  
Ofício DPE CAJ I / FP Saúde nº {numero_oficio}  
Código de Referência nº {numero_triagem}

À SECRETARIA ESTADUAL DE SAÚDE - SESAB/GASEC/ASTEC  
4ª Avenida do Centro Administrativo da Bahia - CAB, nº 400, Salvador - BA, CEP.: 40301-110  

Ilustre Secretário (a) / Diretor (a),


Com cumprimentos cordiais, de ordem da Coordenadora da Especializada de Fazenda Pública, Dra. Raíssa Louzada Lopes Rios Barreto, sirvo-me do presente para encaminhá-lo (a) o OFÍCIO DPE CAJI/FP SAÚDE Nº {numero_oficio}, em favor de **{nome_assistido}**, {nacionalidade}, {estado_civil}, {profissao}, portador (a) do R.G. nº {rg}, inscrito (a) no CPF/MF sob o nº {cpf}, Cartão do SUS anexo, filho (a) de {nome_pai}, neste ato representado por sua genitora, {nome_mae}, inscrito (a) no CPF/MF anexo, residente e domiciliado (a) na {endereco}, telefones de contato: {telefones}, endereço eletrônico: {email}, noticiando a necessidade da realização de **{procedimento}**, conforme relatório médico e documentos que seguem anexos.

Considerando a gravidade das consequências que decorrem da ausência do tratamento ou mesmo da demora na sua disponibilização, com risco iminente à saúde do (a) solicitante, bem como com suporte nos preceitos normativos enunciados no art. 68, X e XI da Lei Complementar Estadual nº 26/06, é que solicita a adoção das providências e medidas administrativas que a situação requer.

Convém informar que, na hipótese de não adoção das medidas de ordem administrativas atinentes à resolução do quadro apresentado, em virtude dos fins institucionais da Defensoria Pública do Estado da Bahia, insta efetuar as providências judiciais adequadas para o cumprimento da lei e da garantia ao assistido (a) do acesso ao seu direito à saúde.

Nesta oportunidade, aguardamos o posicionamento de Vossa Senhoria, no prazo de **{prazo}**, ao passo em que renovamos os protestos de estima e consideração pela pronta atenção dispensada à Defensoria Pública do Estado da Bahia em todas as oportunidades e colocamo-nos sempre à disposição para eventuais esclarecimentos que se afigurem necessários.
    """)
