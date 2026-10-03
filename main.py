"""VFS Shell — эмулятор командной строки UNIX-подобной ОС.

Этап 1: REPL с заглушками ls, cd, exit.
"""


def parse_command(line: str):
    """Разбивает строку на команду и список аргументов по пробелам."""
    parts = line.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]


def cmd_ls(args):
    """Заглушка команды ls."""
    print(f"ls: команда='ls', аргументы={args}")


def cmd_cd(args):
    """Заглушка команды cd."""
    print(f"cd: команда='cd', аргументы={args}")


def process_line(line: str) -> bool:
    """Обрабатывает одну строку. Возвращает False, если нужно выйти."""
    cmd, args = parse_command(line)
    if cmd is None:
        return True

    if cmd == "exit":
        print("Выход.")
        return False
    elif cmd == "ls":
        cmd_ls(args)
    elif cmd == "cd":
        cmd_cd(args)
    else:
        print(f"{cmd}: команда не найдена")
    return True


def repl():
    """Главный цикл: читаем строку — обрабатываем — повторяем."""
    print("VFS Shell v0.1 (этап 1). Введите 'exit' для выхода.")
    while True:
        try:
            line = input("user@vfs:/$ ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not process_line(line):
            break


if __name__ == "__main__":
    repl()