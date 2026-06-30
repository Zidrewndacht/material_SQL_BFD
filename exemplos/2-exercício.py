import sqlite3

DB_NAME = "tarefas.db"

def get_conexao():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    conexao = get_conexao()
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            concluida INTEGER DEFAULT 0
        )
    """)
    conexao.commit()
    conexao.close()

def adicionar_tarefa(descricao):
    conexao = get_conexao()
    with conexao:
        conexao.execute(
            "INSERT INTO tarefas (descricao) VALUES (?)",
            (descricao,)
        )
    conexao.close()
    print(f"Tarefa adicionada: {descricao}")

def listar_tarefas():
    conexao = get_conexao()
    tarefas = conexao.execute("SELECT * FROM tarefas").fetchall()
    conexao.close()

    if not tarefas:
        print("Nenhuma tarefa encontrada.")
        return

    print("\n--- Lista de Tarefas ---")
    for t in tarefas:
        status = "[x]" if t["concluida"] else "[ ]"
        print(f"  {t['id']}. {status} {t['descricao']}")
    print()

def concluir_tarefa(id_tarefa):
    conexao = get_conexao()
    tarefa = conexao.execute(
        "SELECT * FROM tarefas WHERE id = ?", (id_tarefa,)
    ).fetchone()

    if tarefa is None:
        print(f"Tarefa com ID {id_tarefa} não encontrada.")
    else:
        with conexao:
            conexao.execute(
                "UPDATE tarefas SET concluida = 1 WHERE id = ?",
                (id_tarefa,)
            )
        print(f"Tarefa {id_tarefa} marcada como concluída.")
    conexao.close()

if __name__ == "__main__":
    inicializar_banco()

    while True:
        print("1 - Adicionar tarefa")
        print("2 - Listar tarefas")
        print("3 - Concluir tarefa")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            descricao = input("Descricao da tarefa: ")
            adicionar_tarefa(descricao)
        elif opcao == "2":
            listar_tarefas()
        elif opcao == "3":
            try:
                id_tarefa = int(input("ID da tarefa: "))
                concluir_tarefa(id_tarefa)
            except ValueError:
                print("ID invalido. Informe um numero inteiro.")
        elif opcao == "0":
            print("Encerrando.")
            break
        else:
            print("Opção invalida.")