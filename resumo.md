# Resumo: SQL, Modelagem e Python (SQLite e PostgreSQL)

## 1. Terminologia:
*   **DDL (Data Definition Language):** Define a estrutura (*Schema*). `CREATE`, `ALTER`, `DROP`.
*   **DML (Data Manipulation Language):** Manipula os dados. `INSERT`, `UPDATE`, `DELETE`.
*   **DQL (Data Query Language):** Extrai e cruza dados. `SELECT`.
*   **TCL (Transaction Control Language):** Garante atomicidade. `COMMIT`, `ROLLBACK`.

---

## 2. Conexão e Arquitetura
*   **O que faz:** Estabelece o canal entre Python e o SGBD.
*   **SQLite (Embarcado):** O banco é um arquivo local. Sem rede, sem senha.
*   **PostgreSQL (Cliente-Servidor):** Serviço de rede (TCP/IP, porta `5432`). Exige autenticação.

```python
import sqlite3
import psycopg2

# SQLite: Arquivo local (ou ':memory:' para DB temporário na RAM)
conn_lite = sqlite3.connect('banco.db')

# PostgreSQL: Rede, Host, Credenciais
conn_pg = psycopg2.connect(
    host="localhost", port="5432", database="loja_db", 
    user="app_user", password="senha_segura"
)
```

---

## 3. DDL: Tabelas, PKs e Modelagem N:M
*   **O que faz:** Cria tabelas e define Chaves Primárias (PK) para identificação única.
*   **Relacionamento 1:N (Um-para-Muitos):** A Chave Estrangeira (FK) fica na tabela do lado "Muitos".
*   **Relacionamento N:M (Muitos-para-Muitos):** Exige uma **Tabela Associativa** no meio. As duas FKs formam uma **PK Composta**, impedindo fisicamente duplicidade de vínculo.

```sql
-- 1. Tabelas Base (DDL)
CREATE TABLE alunos (id SERIAL PRIMARY KEY, nome TEXT NOT NULL); -- Postgres usa SERIAL, SQLite usa INTEGER PRIMARY KEY AUTOINCREMENT
CREATE TABLE materias (id SERIAL PRIMARY KEY, nome TEXT NOT NULL);

-- 2. Tabela Associativa N:M (O coração do N:M)
CREATE TABLE matriculas (
    aluno_id INTEGER NOT NULL,
    materia_id INTEGER NOT NULL,
    PRIMARY KEY (aluno_id, materia_id), -- PK Composta (Garante unicidade do par)
    FOREIGN KEY (aluno_id) REFERENCES alunos(id),
    FOREIGN KEY (materia_id) REFERENCES materias(id)
);
```
*   **Execução em Python:**
    *   *SQLite:* `cursor.executescript(sql_string)` (apenas `executescript` aceita múltiplos comandos com `;`).
    *   *PostgreSQL:* `cursor.execute(sql_string)` (Não tem `executescript`, `execute` aceita a string com `;`).

---

## 4. Integridade Referencial (FOREIGN KEY)
*   **O que faz:** Impede "dados órfãos" (ex: matricular um aluno inexistente).
*   **A Diferença Crítica:**
    *   *SQLite:* Vem **desligado**. Exige ativação manual por conexão.
    *   *PostgreSQL:* Nativo e **sempre ativo**.

```python
# SQLite: OBRIGATÓRIO ativar logo após conectar
conn_lite.execute("PRAGMA foreign_keys = ON;")

# PostgreSQL: Não requer configuração. A validação é sempre ativa.
```

---

## 5. DML: Inserção Segura e Captura de IDs
*   **O que faz:** Insere dados e recupera o ID gerado para encadear operações.
*   **Segurança (Anti-Injection):** Use *placeholders* para separar código de dados. **Nunca** use *f-strings*.
    *   *SQLite:* Usa **`?`**
    *   *PostgreSQL:* Usa **`%s`** (independente do tipo de dado).

```python
# --- SQLITE ---
cursor_lite.execute("INSERT INTO alunos (nome) VALUES (?)", ("Ana",))
id_ana_lite = cursor_lite.lastrowid # Captura o ID gerado

# --- POSTGRESQL ---
# Cláusula RETURNING devolve a linha inserida
cursor_pg.execute("INSERT INTO alunos (nome) VALUES (%s) RETURNING id", ("Ana",))
id_ana_pg = cursor_pg.fetchone()['id'] # Captura o ID via dicionário
```

---

## 6. DQL: Cruzamentos (JOINs)
*   **O que faz:** Remonta dados normalizados em tabelas separadas.
*   **INNER JOIN:** Interseção. Só retorna se houver match em **ambas**.
*   **LEFT JOIN:** Tabela da esquerda comanda. Retorna **tudo** da esquerda + match da direita (ou `NULL`).

```sql
-- INNER JOIN Duplo (Atravessando a tabela associativa N:M)
SELECT a.nome AS aluno, m.nome AS materia
FROM matriculas mat
INNER JOIN alunos a ON mat.aluno_id = a.id
INNER JOIN materias m ON mat.materia_id = m.id;

-- LEFT JOIN (Listar todos os alunos, mesmo os sem matrícula)
SELECT a.nome, m.nome
FROM alunos a
LEFT JOIN matriculas mat ON a.id = mat.aluno_id
LEFT JOIN materias m ON mat.materia_id = m.id; -- Se não houver matrícula, m.nome será NULL
```

---

## 7. Mapeamento de Resultados (Acesso por Nome)
*   **O que faz:** Transforma tuplas indexadas (`row[0]`) em objetos acessíveis por nome (`row['nome']`).
```python
# SQLite
conn_lite.row_factory = sqlite3.Row
cursor_lite = conn_lite.cursor()

# PostgreSQL
from psycopg2.extras import RealDictCursor
cursor_pg = conn_pg.cursor(cursor_factory=RealDictCursor)

# Uso idêntico após configuração:
for row in cursor.execute("SELECT * FROM alunos"):
    print(row['nome'])
```

---


## 8. TCL: Transações e Ciclo de Vida (`with` vs `finally`)

*   **O Conceito:** Em bancos de dados, você precisa garantir duas coisas:
    1.  **Atomicidade (Transação):** Se der erro no meio de várias operações, desfazer tudo (`ROLLBACK`). Se der tudo certo, salvar (`COMMIT`).
    2.  **Liberação de Recursos (Conexão):** Fechar o canal de rede/arquivo para não vazar memória ou esgotar o *pool* do banco.
*   **A Regra de Ouro:** O bloco `with conexao:` gerencia **apenas a transação**. Ele **NÃO** fecha a conexão. Para fechar a conexão, usamos o bloco `finally`.

```python
conexao = psycopg2.connect(...) # Funciona igual para sqlite3

try:
    # 1. GERENCIAMENTO DE TRANSAÇÃO
    # O 'with' na conexão inicia a transação.
    with conexao:
        cursor = conexao.cursor()
        cursor.execute("UPDATE alunos SET nome = %s WHERE id = %s", ("Ana", 1))
        cursor.execute("INSERT INTO log (...) VALUES (...)")
        
        # Ao sair deste bloco 'with' sem erros, o COMMIT é automático.
        # Se qualquer linha acima falhar, o 'with' intercepta, dá ROLLBACK automático e levanta o erro.

except psycopg2.Error as e:
    # 2. TRATAMENTO DE ERRO
    # Se chegou aqui, o 'with' acima já garantiu que o ROLLBACK foi executado.
    # O banco está íntegro mas a tarefa não foi executada. Agora você apenas registra em log ou trata o erro no Python.
    print(f"Erro de banco de dados: {e}")
    
finally:
    # 3. GERENCIAMENTO DE CONEXÃO (OBRIGATÓRIO)
    # O 'finally' roda sempre (dando erro ou não).
    # É aqui que fechamos a conexão.
    conexao.close() 
```

### 💡 Nota sobre o `with` no Cursor (Boas Práticas)
No `psycopg2`, você verá por aí o uso de `with conexao.cursor() as cursor:`. 
*   **O que ele faz:** Ele **não** gerencia transações. Ele serve apenas para **fechar o cursor** (liberar a memória alocada no servidor para aquela consulta específica) assim que o bloco termina. 
*   **Quando usar:** É útil em aplicações de alta performance com queries pesadas, mas para o dia a dia e para entender o fluxo de transações, instanciar o cursor diretamente (`cursor = conexao.cursor()`) e fechar a conexão no `finally` é o suficiente e muito mais didático.

---

## 9. Ferramentas Visuais (GUI)

### SQLite: DB Browser for SQLite (DB4S)
*   **O que é:** Ferramenta open-source, leve, interface de planilha. Suporta criptografia *SQLCipher*.
*   **Status Atual:** Versão estável **3.13.0** (Binários Windows com assinatura de código via *SignPath.io*).
*   **Regra de Ouro:** Certifique-se de que a conexão Python esteja fechada (`conn.close()`) antes de editar o arquivo `.db` na ferramenta para evitar o erro `database is locked` (concorrência de acesso ao arquivo).

### PostgreSQL: pgAdmin 4
*   **O que é:** Interface web local robusta com Query Tool, autocompletar e dashboards.
*   **Instalação Windows:** Obtido via **Interactive installer by EDB** (Hospedado pela EnterpriseDB, não nos servidores da comunidade). Configura o Postgres como serviço do Windows.
*   **Suporte de Plataforma (EDB):** Testado em Windows Server 2025/2022 (para Postgres 18) e 2022/2019 (para Postgres 17/16).



## 20: Tabela Comparativa de Referência Rápida

| Operação | SQLite (`sqlite3`) | PostgreSQL (`psycopg2`) |
| :--- | :--- | :--- |
| Instalar driver | Nativo (zero setup) | `pip install psycopg2-binary` |
| Conectar | `sqlite3.connect("arquivo.db")` | `psycopg2.connect(host, port, database, user, password)` |
| Auto-incremento | `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` |
| Placeholder | `?` | `%s` |
| Acesso por nome | `conexao.row_factory = sqlite3.Row` | `cursor_factory=RealDictCursor` |
| Capturar ID inserido | `cursor.lastrowid` | `RETURNING id` + `fetchone()` |
| Ativar FK | `PRAGMA foreign_keys = ON` | Nativo (sempre ativo) |
| Múltiplos comandos | `cursor.executescript(...)` | `cursor.execute(...)` (um por vez ou separado por `;`) |
| Erro de integridade | `sqlite3.IntegrityError` | `psycopg2.IntegrityError` |
| Rollback após erro | Automático no `with` | Manual: `conexao.rollback()` |
| Banco em memória | `sqlite3.connect(":memory:")` | Não suportado (requer servidor) |
| Ferramenta visual | DB Browser for SQLite | pgAdmin 4 / DBeaver |
