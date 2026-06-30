import sqlite3

conexao = sqlite3.connect("escola.db")
conexao.row_factory = sqlite3.Row
conexao.execute("PRAGMA foreign_keys = ON;")
cursor = conexao.cursor()

# 1. Criação do Schema (DDL)
cursor.executescript("""
    CREATE TABLE IF NOT EXISTS alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL
    );
    
    -- Tabela Associativa (O coração do relacionamento N:M)
    CREATE TABLE IF NOT EXISTS matriculas (
        aluno_id INTEGER NOT NULL,
        materia_id INTEGER NOT NULL,
        -- PRIMARY KEY Composta: A combinação dos dois IDs deve ser única.
        -- Impede duplicidade de matrícula do mesmo aluno na mesma matéria.
        PRIMARY KEY (aluno_id, materia_id),
        -- Dupla integridade referencial: Ambos os IDs devem existir em suas respectivas tabelas.
        FOREIGN KEY (aluno_id) REFERENCES alunos(id),
        FOREIGN KEY (materia_id) REFERENCES materias(id)
    );
""")

# 2. Inserção de Entidades (DML)
cursor.execute("INSERT INTO alunos (nome) VALUES (?)", ("Carlos",))  # ID 1
cursor.execute("INSERT INTO alunos (nome) VALUES (?)", ("Ana",))     # ID 2

cursor.execute("INSERT INTO materias (nome) VALUES (?)", ("Python Avançado",)) # ID 1
cursor.execute("INSERT INTO materias (nome) VALUES (?)", ("Banco de Dados",))  # ID 2
conexao.commit()

# 3. Inserção dos Relacionamentos (Matriculando)
# Carlos (1) cursa Python (1) e Banco de Dados (2)
# Ana (2) cursa apenas Banco de Dados (2)
# 'executemany' insere múltiplas tuplas de uma vez.
cursor.executemany(
    "INSERT INTO matriculas (aluno_id, materia_id) VALUES (?, ?)",
    [
        (1, 1), 
        (1, 2), 
        (2, 2)
    ]
)
conexao.commit()

# 4. Consulta Cruzada (DQL com JOIN Duplo)
print("--- Grade Curricular ---")
query = """
    -- SELECT: Escolhe as colunas finais, usando 'AS' para criar apelidos (aliases) claros.
    SELECT a.nome AS aluno, m.nome AS materia
    -- FROM: A consulta começa pela tabela associativa (a "ponte").
    FROM matriculas mat
    -- JOIN 1: Conecta a ponte à tabela de alunos usando o ID do aluno.
    JOIN alunos a ON mat.aluno_id = a.id
    -- JOIN 2: Conecta a ponte à tabela de matérias usando o ID da matéria.
    JOIN materias m ON mat.materia_id = m.id
    -- ORDER BY: Ordena o resultado final alfabeticamente pelo nome do aluno.
    ORDER BY a.nome;
"""

for row in cursor.execute(query).fetchall():
    print(f"Aluno: {row['aluno']} | Matéria: {row['materia']}")

conexao.close()