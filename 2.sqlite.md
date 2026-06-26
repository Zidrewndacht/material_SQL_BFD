
## 3: O SQLite

Os DBMS podem ser classificados de acordo com sua arquitetura:

1.  **Bancos Embarcados (Serverless):** O motor do banco roda dentro do próprio processo da aplicação. O banco é um arquivo no disco. (Ex: **SQLite**).
2.  **Servidores Dedicados (Client-Server):** O banco é um serviço independente, escutando em uma porta de rede, gerenciando múltiplos clientes. (Ex: PostgreSQL, MySQL).
3.  **Bancos Distribuídos:** Dados fragmentados em múltiplos nós para escala massiva. (Ex: Cassandra).

É um equívoco comum tratar o SQLite como um "banco de brinquedo". Na realidade, o SQLite é o **DBMS mais implantado do mundo**, superando em números absolutos a soma de todos os outros bancos de dados combinados.

A distinção fundamental está na **Arquitetura**:

| Característica | SQLite (Banco Embarcado / *In-Process*) | PostgreSQL / MySQL (Cliente-Servidor) |
| :--- | :--- | :--- |
| **Arquitetura** | O motor do banco é uma biblioteca embutida no próprio aplicativo. | O banco é um serviço independente rodando em um servidor de rede. |
| **Comunicação** | Chamadas de função diretas na memória do processo. | Protocolo de rede (TCP/IP), exigindo autenticação e sockets. |
| **Armazenamento** | Um único arquivo comum no sistema de arquivos do SO. | Múltiplos arquivos gerenciados exclusivamente pelo processo do servidor. |
| **Caso de Uso Ideal** | Acesso local, aplicativos desktop/mobile, edge computing, IoT. | Múltiplos clientes acessando e escrevendo simultaneamente via rede. |

### Onde o SQLite é usado no Mundo Real?
O SQLite está em aplicações usadas diariamente:

1.  **Aplicativos de Mensagens (WhatsApp, Telegram, Signal):** Todo o seu histórico de mensagens, contatos, metadados de grupos e configurações locais são armazenados em bancos de dados SQLite (frequentemente criptografados com extensões como *SQLCipher*) no armazenamento interno do seu celular.
2.  **Navegadores Web (Chrome, Firefox, Safari, Edge):** O histórico de navegação, os cookies, o cache de DNS, os favoritos e as senhas salvas localmente são gerenciados por múltiplos arquivos SQLite.
3.  **Sistemas Operacionais Móveis:** O **Android** e o **iOS** fornecem APIs nativas para SQLite. O framework *Core Data* da Apple, utilizado em milhões de aplicativos na App Store, é, em sua essência, um gerenciador de objetos construído sobre o SQLite.
4.  **Softwares Desktop e Criativos:** Adobe Photoshop, Lightroom, Autodesk AutoCAD e Skype utilizam SQLite para salvar catálogos, estados de projetos e configurações de usuário devido à sua extrema confiabilidade e atomicidade.
5.  **Indústria Aeroespacial e Automotiva:** Sistemas de entretenimento de bordo, telemetria de veículos e softwares de manutenção de aeronaves (como os da Airbus) utilizam SQLite devido à sua capacidade de operar sem configuração de rede e com altíssima tolerância a falhas.

**Conclusão Arquitetural:** A escolha entre SQLite e PostgreSQL não é uma progressão de "iniciante para avançado". É uma decisão de engenharia: se o seu aplicativo precisa gerenciar seus próprios dados localmente, o SQLite é a escolha de nível de produção. Para aplicações Web com pouca concorrência de usuários, SQLite pode também ser perfeitamente adequado. Se o seu aplicativo precisa servir dados para milhares de usuários simultâneos através da internet, um DBMS Cliente-Servidor costuma ser preferível.

---

## 4: Integração com Python (`sqlite3`) e Segurança

A comunicação entre o Python e o SQLite ocorre através do módulo nativo `sqlite3`, utilizando dois objetos principais: a **Conexão** e o **Cursor**.

### 4.1 Conexão e Cursor
```python
import sqlite3

# Estabelece a conexão com o arquivo. Se não existir, o arquivo é criado.
conexao = sqlite3.connect('loja.db')

# O cursor é a interface através da qual os comandos SQL são executados.
cursor = conexao.cursor()
```

> **Nota técnica sobre testes:** Para testes unitários ou experimentações rápidas, é possível criar um banco de dados volátil na memória RAM, que é destruído ao fechar a conexão:
> `conexao = sqlite3.connect(':memory:')`

### 4.2 Definição de Estrutura (DDL)
```python
# O comando IF NOT EXISTS previne erros em execuções subsequentes.
sql_criacao = """
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    estoque INTEGER DEFAULT 0
)
"""
cursor.execute(sql_criacao)
```

### 4.3 Manipulação de Dados (DML) e o Risco de SQL Injection

A inserção de dados exige rigor técnico quanto à segurança. A concatenação de strings (como *f-strings*) para montar queries é uma vulnerabilidade crítica catalogada como **SQL Injection** (Injeção de SQL).

A cultura de desenvolvimento ilustra esse risco com uma famosa tirinha do XKCD chamada *"Exploits of a Mom"*. Na história, uma escola liga para a mãe de um aluno questionando o nome registrado da criança no sistema: `Robert'); DROP TABLE Students;--`.

Se o sistema da escola utilizar concatenação ingênua, o código Python montará a string SQL antes de enviá-la ao banco, resultando em uma catástrofe.

#### ❌ A Prática Insegura (O Cenário do XKCD)

Neste exemplo, simulamos o código vulnerável da escola:

```python
# A entrada do usuário (o nome do aluno)
nome_aluno = "Robert'); DROP TABLE Students;--"

# O programador monta a query concatenando a string diretamente
query = f"INSERT INTO Students (nome) VALUES ('{nome_aluno}')"

# A string resultante que o banco receberá é:
# "INSERT INTO Students (nome) VALUES ('Robert'); DROP TABLE Students;--')"

# O motor do banco interpretará isso como TRÊS instruções distintas:
# 1. INSERT INTO Students (nome) VALUES ('Robert');  -> Insere o aluno Robert
# 2. DROP TABLE Students;                            -> APAGA A TABELA INTEIRA
# 3. --')"                                           -> Tratado como comentário, ignorado.

cursor.executescript(query)
# Note o uso de `executescript`, que permite a execução de múltiplos comandos separados por ponto e vírgula (comportamento comum em várias linguagens e drivers de banco de dados).
```

#### ✅ A Prática Segura (Queries Parametrizadas)

Para neutralizar esse vetor de ataque, utilizamos *placeholders* (`?`). O driver do `sqlite3` assume a responsabilidade de sanitizar e escapar os dados, tratando a entrada estritamente como um valor literal, nunca como código executável.

```python
# A mesma entrada maliciosa
nome_aluno = "Robert'); DROP TABLE Students;--"

# A query contém apenas o marcador de posição (?)
query = "INSERT INTO Students (nome) VALUES (?)"

# O driver do sqlite3 escapa as aspas e caracteres especiais automaticamente.
# O banco armazena a string exata como o nome do aluno.
cursor.execute(query, (nome_aluno,))

# Resultado no banco:
# A tabela Students permanece intacta.
# Existe um aluno cujo nome é literalmente: "Robert'); DROP TABLE Students;--"
```

**Conclusão Técnica:** A parametrização separa o **código** (a estrutura do SQL) dos **dados** (os valores fornecidos pelo usuário). Isso torna matematicamente impossível que dados de entrada alterem a lógica da query, blindando a aplicação contra injeções.


### 4.4 Leitura e Mapeamento de Resultados
Por padrão, o SQLite retorna tuplas, o que exige conhecimento prévio da **ordem das colunas**. A propriedade `row_factory` altera esse comportamento para retornar objetos acessíveis por nome de coluna, assemelhando-se a dicionários (ideal para quem vem do consumo de APIs JSON).

```python
conexao.row_factory = sqlite3.Row
cursor = conexao.cursor()

cursor.execute("SELECT * FROM produtos WHERE preco > ?", (1000.0,))
resultados = cursor.fetchall()

for row in resultados:
    print(f"Produto: {row['nome']} | Preço: {row['preco']}")
```

### 4.5 Transações e Gerenciadores de Contexto (`with`)
No Python, a instrução `with` invoca um padrão de projeto chamado **Gerenciador de Contexto** (*Context Manager*). Seu propósito é garantir que recursos tenham uma fase de "preparação" e uma fase de "limpeza" (teardown), independentemente de o código interno falhar ou não.

No módulo `sqlite3`, é fundamental compreender uma distinção técnica: **o bloco `with` na conexão gerencia transações, mas não fecha a conexão com o banco.**

Por baixo dos panos, o Python traduz o bloco `with` para uma estrutura de exceções que garante a **atomicidade** (a regra do "tudo ou nada"):

```python
# O que você escreve:
with conexao:
    conexao.execute("UPDATE produtos SET estoque = estoque - 1 WHERE id = ?", (1,))
    conexao.execute("UPDATE vendas SET total = total + 1 WHERE id = ?", (5,))

# O que o Python executa por baixo dos panos (equivalente lógico):
try:
    conexao.execute("BEGIN")  # Inicia a transação
    conexao.execute("UPDATE produtos SET estoque = estoque - 1 WHERE id = ?", (1,))
    conexao.execute("UPDATE vendas SET total = total + 1 WHERE id = ?", (5,))
    conexao.commit()          # Se tudo passar, salva no disco
except Exception:
    conexao.rollback()        # Se qualquer linha falhar, desfaz TUDO
    raise                     # Propaga o erro para o programa
```
*Nota: O método `conexao.close()` ainda deve ser chamado explicitamente ao final do ciclo de vida da aplicação para liberar o arquivo no Sistema Operacional.*

---


## 5: Exemplo Guiado - Catálogo de Livros

**Cenário:** Criar um banco de dados em memória (`:memory:`) para armazenar um pequeno catálogo de livros, inserir dois registros e exibi-los no terminal.

> **Nota:** O arquivo `catalogo.db` será criado na pasta do projeto e poderá ser inspecionado posteriormente com o DB Browser for SQLite (Bloco 7). Executar o script múltiplas vezes inserirá registros duplicados, pois não fizemos nenhuma verificação de existência. Para reiniciar, basta apagar o arquivo `.db`.

```python
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

# 3. Inserir dados (DML parametrizado)
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
```

## 6: Desafio Prático - Gerenciador de Tarefas (CLI com Interação)

**Objetivo:** Desenvolver uma aplicação interativa de linha de comando para gerenciamento de tarefas, aplicando os conceitos de DDL, DML, parametrização, transações com `with` e tratamento de exceções.

**Requisitos:**
1. Criar funções para: `inicializar_banco()`, `adicionar_tarefa()`, `listar_tarefas()` e `concluir_tarefa()`.
2. O banco deve ser salvo em disco (`tarefas.db`) para inspeção com o DB Browser.
3. O programa deve apresentar um menu com `input()` permitindo que o usuário escolha a ação desejada.
4. Utilizar `with conexao:` para operações de escrita.
5. Utilizar `fetchone()` para verificar se uma tarefa existe antes de atualizá-la.

**Estrutura sugerida:**
```python
import sqlite3

DB_NAME = "tarefas.db"

def get_conexao():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    # ...

def inicializar_banco():
    # CREATE TABLE IF NOT EXISTS ...

def adicionar_tarefa(descricao):
    # INSERT parametrizado com with ...

def listar_tarefas():
    # SELECT * ...

# ...

if __name__ == "__main__":
    inicializar_banco()
    # Loop com input() para o menu ...
```

## Bloco 7: Inspeção Visual com DB Browser for SQLite

Como o SQLite armazena o banco de dados inteiro em um único arquivo comum no sistema de arquivos (`.db` ou `.sqlite`), é frequentemente necessário inspecionar seu conteúdo sem escrever queries Python.

Para isso, a indústria utiliza o **DB Browser for SQLite** (anteriormente conhecido como SQLiteBrowser).
*   **Link Oficial:** [sqlitebrowser.org](https://sqlitebrowser.org/)
*   **O que é:** Uma aplicação desktop de código aberto, leve e visual, projetada para criar, projetar e editar arquivos de banco de dados SQLite.
*   **Como utilizar:**
    1. Abra o DB Browser e selecione "Open Database" (Abrir Banco de Dados).
    2. Navegue até o arquivo `.db` gerado pelo seu script Python.
    3. Na aba **"Database Structure"**, você pode visualizar o Schema (tabelas, colunas e tipos).
    4. Na aba **"Browse Data"**, é possível visualizar, filtrar e editar as linhas das tabelas através de uma interface semelhante a uma planilha.
    5. Na aba **"Execute SQL"**, você pode testar queries complexas com autocompletar antes de portá-las para o código Python.

*Nota técnica: Certifique-se de que seu script Python não esteja rodando (ou que a conexão esteja fechada) ao tentar fazer alterações estruturais pelo DB Browser, para evitar erros de "banco travado" (database is locked) devido à concorrência de acesso ao arquivo.*

---

## Resumo e Boas Práticas

1.  **Persistência exige estrutura:** Variáveis são voláteis. Um DBMS garante sobrevivência, integridade e controle de concorrência para os dados.
2.  **Modelagem Relacional:** Utilize Chaves Primárias para identificação única e Chaves Estrangeiras para estabelecer relacionamentos lógicos, evitando redundância.
3.  **Paradigma Declarativo:** Em SQL, defina o resultado esperado (`SELECT`), não o algoritmo de busca. O motor do banco otimizará a operação.
4.  **Segurança em Primeiro Lugar:** Jamais concatene strings para formar queries SQL. Utilize exclusivamente queries parametrizadas (`?`) para prevenir *SQL Injection*.
5.  **Mapeamento de Dados:** Configure `row_factory = sqlite3.Row` para acessar resultados de consultas através do nome das colunas, facilitando a integração com estruturas de dicionários e JSON.
6.  **Atomicidade:** Utilize o gerenciador de contexto (`with conexao:`) para garantir que operações compostas sejam tratadas como transações indivisíveis.
7.  **Arquitetura Consciente:** Entenda que o SQLite é um DBMS de nível de produção para cenários embarcados e locais. A migração para bancos Cliente-Servidor (como PostgreSQL) ocorre quando a arquitetura do sistema exige acesso concorrente via rede.
8.  **Combata SQL Injection:** Jamais concatene strings para formar queries. O uso de *placeholders* (`?`) delega a sanitização ao driver, neutralizando injeções de código (como o ataque "Little Bobby Tables").
9.  **Compreenda o `with`:** No `sqlite3`, o Gerenciador de Contexto (`with conexao:`) garante a atomicidade das transações (`commit` ou `rollback`), mas **não** encerra a conexão. O `close()` manual é obrigatório.
10. **Utilize Ferramentas Visuais:** O **DB Browser for SQLite** é a ferramenta padrão para inspecionar, depurar e validar a estrutura e os dados do seu arquivo `.db` fora do ambiente de código.

### Próximos Passos
*   Aprofundamento em Relacionamentos (`JOINs`, `LEFT JOIN`, Integridade Referencial).
*   Migração para SGBDs Client-Server (PostgreSQL), configuração de rede e ORMs (Mapeamento Objeto-Relacional).
*   Bancos NoSQL e cenários onde o modelo relacional não é a escolha ideal.
