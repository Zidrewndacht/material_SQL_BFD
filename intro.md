# Fundamentos de Bancos de Dados Relacionais e SQL

**Pré-requisitos:** Estruturas de dados, Funções, Tratamento de Exceções e Manipulação de Arquivos.  
**Ambiente:** Python Standard Library (módulo `sqlite3`).

---

## 0: O Problema da Persistência e o Papel dos bancos de dados

### O que já sabemos até aqui
Até este momento, nosso ecossistema de desenvolvimento contempla as seguintes camadas:

| Linguagem / Ferramenta | Propósito | Onde os dados residem? |
| :--- | :--- | :--- |
| **HTML / CSS** | Estruturação e apresentação visual. | No navegador do cliente (temporário). |
| **Python** | Lógica de negócio, automação e processamento. | Na memória RAM (volátil). |
| **HTTP / APIs** | Transporte de dados entre cliente e servidor. | Em trânsito pela rede. |

### O problema da volatilidade
Variáveis em Python existem apenas durante o tempo de vida do processo. Se o script for encerrado, o sistema reiniciado ou ocorrer uma falha, os dados em memória são perdidos.

```python
# Estado da aplicação em memória
tarefas = ["Estudar Python", "Fazer exercícios", "Revisar SQL"]
# Se o processo terminar, a lista deixa de existir.
```

**Persistência** é a capacidade de um sistema manter dados disponíveis e íntegros após o término do programa que os criou.

### Soluções ingênuas e suas limitações
Uma abordagem inicial para persistência é o uso de arquivos planos (`.txt`, `.csv`, `.json`). No entanto, em cenários de produção, essas soluções apresentam falhas graves:
1.  **Busca ineficiente:** Para filtrar registros, é necessário carregar todo o arquivo na memória RAM e iterar sobre ele.
2.  **Concorrência:** Se dois processos tentarem escrever no mesmo arquivo simultaneamente, ocorrerá corrupção de dados (condição de corrida).
3.  **Falta de integridade:** Não há mecanismo nativo que impeça a inserção de um pedido referenciando um cliente inexistente.

### A solução profissional: DBMS / SGBD
Um **DBMS** (*Database Management System*), ou **SGBD** (Sistema Gerenciador de Banco de Dados) em português, é um software de alta complexidade projetado para resolver esses problemas. Suas responsabilidades incluem:
*   **Armazenamento estruturado e eficiente** em disco.
*   **Recuperação rápida** através de índices (estruturas de dados como B-Trees) e algoritmos de busca.
*   **Garantia de integridade** por meio de regras estritas (*constraints*).
*   **Controle de concorrência** para permitir múltiplos acessos simultâneos sem corrupção.
*   **Transações (ACID):** Garantia de que um conjunto de operações ocorra por completo ou não ocorra (Atomicidade), mantendo a consistência dos dados mesmo em caso de falhas de hardware.

---

## 1: O Modelo Relacional

O Modelo Relacional organiza dados em estruturas bidimensionais (tabelas) que se conectam através de identificadores comuns.

### Estrutura de um Banco Relacional
```text
Banco de Dados: "loja_online"
├── Tabela: clientes
│   ├── id (inteiro, único, automático) 
│   ├── nome (texto, obrigatório)
│   └── email (texto, único)
│
├── Tabela: produtos
│   ├── id (inteiro, único, automático)
│   ├── nome (texto)
│   └── preco (número decimal)
│
└── Tabela: pedidos
    ├── id (inteiro, único, automático)
    ├── cliente_id (inteiro -> referencia clientes.id)
    ├── produto_id (inteiro -> referencia produtos.id)
    └── quantidade (inteiro)
```

### Conceitos Fundamentais

| Termo | Definição Técnica |
| :--- | :--- |
| **Tabela (Table)** | Entidade que armazena registros de um mesmo tipo. |
| **Coluna (Column)** | Atributo da entidade, possuindo tipo de dado e regras de validação. |
| **Linha (Row)** | Um registro concreto e individual inserido na tabela. |
| **Chave Primária (PK)** | Identificador único e intransferível para cada linha (ex: `id`). |
| **Chave Estrangeira (FK)** | Coluna que estabelece uma ligação com a Chave Primária de outra tabela. |
| **Schema** | A estrutura lógica do banco (definição de tabelas, tipos e relacionamentos). |

### A Natureza "Relacional"
O termo refere-se à capacidade de cruzar dados entre tabelas distintas. Em vez de duplicar o nome do cliente em cada pedido, armazenamos apenas o `cliente_id`. A recuperação dos dados completos é feita através de operações de junção (`JOIN`):

```sql
SELECT clientes.nome, produtos.nome, pedidos.quantidade
FROM pedidos
JOIN clientes ON pedidos.cliente_id = clientes.id
JOIN produtos ON pedidos.produto_id = produtos.id;
```
Esta operação consolida informações de três origens distintas em um único resultado, garantindo que, se o nome do cliente for atualizado na tabela `clientes`, todos os seus pedidos refletirão a mudança automaticamente.

---

## 2: A Linguagem SQL e o Paradigma Declarativo

**SQL** (*Structured Query Language*) é a linguagem padrão para interação com bancos relacionais. Diferente das linguagens de programação de propósito geral, SQL opera sob um paradigma distinto.

### Imperativo vs. Declarativo

| Característica | Python (Imperativo) | SQL (Declarativo) |
| :--- | :--- | :--- |
| **Foco** | Descreve **como** realizar uma tarefa (passo a passo). | Descreve **o que** se deseja obter (o resultado final). |
| **Execução** | Sequencial, controlada pelo programador. | Otimizada pelo motor do DBMS (*engine*). |
| **Exemplo** | Iterar sobre uma lista e aplicar um `if`. | `SELECT * FROM tabela WHERE condicao;` |

**Comparação Prática:**
```python
# Python: O programador define a lógica de iteração e filtragem
produtos_caros = []
for produto in lista_de_produtos:
    if produto["preco"] > 1000:
        produtos_caros.append(produto)
```

```sql
-- SQL: O programador define o critério; o banco decide como buscar
SELECT * FROM produtos WHERE preco > 1000;
```

### Universalidade
SQL é padronizada (ANSI/ISO), o que significa que a sintaxe fundamental é aplicável na grande maioria dos DBMS do mercado. O conhecimento adquirido é, portanto, altamente transferível entre diferentes tecnologias.
