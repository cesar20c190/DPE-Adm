import sqlite3

# Conectar ao banco
conn = sqlite3.connect("banco_termos.db")
cursor = conn.cursor()

# Tabela principal: termos
cursor.execute("""
CREATE TABLE IF NOT EXISTS termos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_termo TEXT,
    regional TEXT,
    cidade_atendimento TEXT,
    nome TEXT,
    cpf TEXT,
    rua TEXT,
    numero TEXT,
    bairro TEXT,
    cidade_assistido TEXT,
    telefone TEXT,
    data_nascimento TEXT,
    sexo TEXT,
    grupo_etnico TEXT,
    renda_individual TEXT,
    renda_familiar TEXT,
    materia TEXT,
    declaracao TEXT
)
""")

# Tabela de demandas vinculadas ao termo
cursor.execute("""
CREATE TABLE IF NOT EXISTS demandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_termo INTEGER,
    tipo TEXT,
    descricao TEXT,
    FOREIGN KEY (id_termo) REFERENCES termos(id)
)
""")

conn.commit()
conn.close()
