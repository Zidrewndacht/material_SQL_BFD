import sqlite3

# 1. Conectar ao banco em disco
conexao = sqlite3.connect("catalogo.db")
conexao.row_factory = sqlite3.Row
cursor = conexao.cursor()

# 2. Criar tabela (DDL)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        ano_publicacao INTEGER
    )
""")

# 3. Inserir dados:
cursor.execute(
    "INSERT INTO livros (titulo, autor, ano_publicacao) VALUES (?, ?, ?)",
    ("O Senhor dos Anéis", "J.R.R. Tolkien", 1954)
)
cursor.execute(
    "INSERT INTO livros (titulo, autor, ano_publicacao) VALUES (?, ?, ?)",
    ("1984", "George Orwell", 1949)
)
cursor.execute(
    "INSERT INTO livros (titulo, autor, ano_publicacao) VALUES (?, ?, ?)",
    ("O Código Da Vinci", "Dan Brown", 2003) # Livro do Século XXI
)
conexao.commit()

# Alternativa: 
# catalogo = [
#     ("O Senhor dos Anéis", "J.R.R. Tolkien", 1954),
#     ("1984", "George Orwell", 1949),
#     ("Dom Casmurro", "Machado de Assis", 1899)
# ]

# # executemany itera sobre a lista de tuplas automaticamente
# cursor.executemany(
#     "INSERT INTO livros (titulo, autor, ano_publicacao) VALUES (?, ?, ?)", 
#     catalogo
# )

# 4. Consultar dados (DQL)
# O uso do AND restringe o resultado estritamente ao intervalo do Século XX
cursor.execute(
    "SELECT * FROM livros WHERE ano_publicacao >= ? AND ano_publicacao <= ?", 
    (1900, 2000)
)

print("--- Livros do Século XX (1900-2000) ---")
for livro in cursor.fetchall():
    print(f"{livro['titulo']} ({livro['ano_publicacao']}) - {livro['autor']}")

# 5. Encerrar conexão
conexao.close()