import sqlite3

# Conecta ou cria o banco de dados local
conexao = sqlite3.connect("banco_termos.db")
cursor = conexao.cursor()

# Cria a tabela 'termos' se ainda não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS termos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    cpf TEXT,
    data TEXT,
    cidade TEXT,
    declaracao TEXT
)
""")

# Salva e fecha a conexão
conexao.commit()
conexao.close()

print("✅ Banco de dados criado com sucesso.")
