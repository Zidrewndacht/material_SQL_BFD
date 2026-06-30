import sqlite3

# Estabelece a conexão com o arquivo. Se não existir, o arquivo é criado em disco.
conexao = sqlite3.connect("loja.db")
# Configura o retorno das consultas para se comportar como dicionários (permitindo acesso por nome de coluna).
conexao.row_factory = sqlite3.Row

# 1. Ativar Integridade Referencial
# PRAGMA é um comando especial do SQLite para alterar configurações da sessão atual.
# 'foreign_keys = ON' instrui o motor do banco a validar ativamente as regras de Chave Estrangeira.
conexao.execute("PRAGMA foreign_keys = ON;")
cursor = conexao.cursor()

# 2. Criação do Schema
# 'executescript' permite a execução de múltiplos comandos SQL separados por ponto e vírgula.
# O DROP TABLE garante que o ambiente esteja limpo a cada execução do script.
cursor.executescript("""
    -- DROP TABLE IF EXISTS pedidos;
                     -- Em bancos com PRAGMA foreign_keys = ON, você deve sempre apagar primeiro as tabelas que 
                     -- possuem a Chave Estrangeira (pedidos) antes de apagar a tabela pai (clientes), caso contrário 
                     -- o DBMS bloqueará a exclusão para proteger a integridade referencial.
    -- DROP TABLE IF EXISTS clientes;
    
    -- CREATE TABLE IF NOT EXISTS: Cria a estrutura da tabela apenas se ela ainda não existir no banco.
    CREATE TABLE IF NOT EXISTS clientes (
        -- INTEGER PRIMARY KEY AUTOINCREMENT: Cria um ID numérico único que sobe automaticamente a cada inserção.
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        -- TEXT NOT NULL: Define a coluna como texto e proíbe o cadastro de valores nulos (vazios).
        nome TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        -- Coluna que guardará a referência (Chave Estrangeira) ao cliente dono do pedido.
        cliente_id INTEGER NOT NULL,
        produto TEXT NOT NULL,
        -- FOREIGN KEY ... REFERENCES: A regra de integridade referencial.
        -- Garante que o valor inserido em 'cliente_id' exista obrigatoriamente na coluna 'id' da tabela 'clientes'.
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    );
""")

# 3. Inserção de Dados
# INSERT INTO ... VALUES: Adiciona uma nova linha à tabela.
# O símbolo (?) é o placeholder de segurança. O valor real é passado via tupla no segundo argumento,
# delegando ao driver do SQLite a tarefa de sanitizar a string e evitar SQL Injection.
# A vírgula é necessária para garantir que Python vai interpretar o valor como uma tupla, mesmo que tenha apenas um dado.
cursor.execute("INSERT INTO clientes (nome) VALUES (?)", ("Ana Silva",))
cursor.execute("INSERT INTO clientes (nome) VALUES (?)", ("Bruno Costa",))
# COMMIT: A instrução que efetiva as mudanças. Sem ela, os dados ficam apenas na memória temporária (cache) do SQLite.
conexao.commit()

# Inserindo pedidos e vinculando ao ID 1 (que corresponde à Ana Silva)
# aqui a vírgula no final não é necessária, pois as vírgulas entre os itens já definem a tupla.
cursor.execute("INSERT INTO pedidos (cliente_id, produto) VALUES (?, ?)", (1, "RTX 5070Ti"))
cursor.execute("INSERT INTO pedidos (cliente_id, produto) VALUES (?, ?)", (1, "2x16GB DDR5-6400"))
conexao.commit()

# 4. Teste de Integridade (O banco deve impedir a inserção órfã)
try:
    # Tentativa de inserir um pedido para o cliente_id 99.
    # Como o PRAGMA está ativo e o ID 99 não existe na tabela 'clientes', o SGBD bloqueará a ação.
    cursor.execute("INSERT INTO pedidos (cliente_id, produto) VALUES (?, ?)", (99, "Monitor"))
    conexao.commit()
except sqlite3.IntegrityError as e:
    print(f"[Integridade] Bloqueado: {e}")

# 5. Consultas com Cruzamento de Dados (DQL)
print("\n--- INNER JOIN (Apenas clientes que possuem pedidos) ---")
query_inner = """
    -- SELECT: Define quais colunas comporão o resultado final da consulta.
    -- Os prefixos 'c.' e 'p.' indicam de qual tabela cada coluna deve ser extraída.
    SELECT c.nome, p.produto 
    -- FROM: Estabelece a tabela principal (base) da consulta, criando o apelido (alias) 'c' para 'clientes'.
    FROM clientes c
    -- INNER JOIN: Solicita o cruzamento com a tabela 'pedidos' (apelidada de 'p').
    -- A palavra INNER dita que apenas as linhas com correspondência exata em AMBAS as tabelas serão retornadas.
    -- ON: Define a condição matemática do cruzamento (o 'id' do cliente deve bater com o 'cliente_id' do pedido).
    INNER JOIN pedidos p ON c.id = p.cliente_id
"""
# fetchall(): Executa a query e recupera todas as linhas resultantes de uma vez.
for row in cursor.execute(query_inner).fetchall():
    print(f"{row['nome']} comprou: {row['produto']}")

print("\n--- LEFT JOIN (Todos os clientes, tendo pedidos ou não) ---")
query_left = """
    SELECT c.nome, p.produto 
    FROM clientes c
    -- LEFT JOIN: Traz TODOS os registros da tabela da esquerda ('clientes'),
    -- independentemente de haver correspondência na tabela da direita ('pedidos').
    -- Se o cliente não tiver feito compras, a coluna 'p.produto' retornará com o valor NULL.
    LEFT JOIN pedidos p ON c.id = p.cliente_id
"""
for row in cursor.execute(query_left).fetchall():
    # Tratamento no Python para exibir uma mensagem amigável caso o banco retorne NULL na coluna do produto.
    produto = row['produto'] if row['produto'] else "Nenhum pedido registrado"
    print(f"{row['nome']} | {produto}")

# CLOSE: Encerra a conexão, liberando o arquivo 'loja.db' de volta para o Sistema Operacional.
conexao.close()