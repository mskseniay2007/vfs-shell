"""VFS Shell — эмулятор командной строки UNIX-подобной ОС."""

import argparse


def parse_command(line):
    """Принимает строку, возвращает (команда, [аргументы])."""
    parts = line.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]


def cmd_ls(args):
    """Заглушка: печатает, что получила команду ls."""
    print(f"ls: команда='ls', аргументы={args}")


def cmd_cd(args):
    """Заглушка: печатает, что получила команду cd."""
    print(f"cd: команда='cd', аргументы={args}")


def process_line(line):
    """Разбирает строку и решает, что делать. Возвращает True/False."""
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


def parse_args():
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(description="Эмулятор shell с VFS")
    parser.add_argument("--vfs", help="Путь к JSON-файлу VFS")
    parser.add_argument("--script", help="Путь к стартовому скрипту")
    return parser.parse_args()


def run_script(path, handle_line):
    """Читает файл скрипта и вызывает handle_line для каждой команды."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")
                if not line.strip():
                    continue
                if line.lstrip().startswith("#"):
                    continue
                print(f"user@vfs:/$ {line}")
                if not handle_line(line):
                    break
    except FileNotFoundError:
        print(f"Ошибка: файл скрипта '{path}' не найден.")
    except Exception as e:
        print(f"Ошибка при выполнении скрипта: {e}")


def repl():
    """Главный цикл: спрашиваем — обрабатываем — спрашиваем снова."""
    print("VFS Shell v0.1 (этап 2). Введите 'exit' для выхода.")

    while True:
        try:
            line = input("user@vfs:/$ ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not process_line(line):
            break


def main():
    """Точка входа: разбираем аргументы и решаем, что делать."""
    args = parse_args()

    print(f"[DEBUG] VFS: {args.vfs}")
    print(f"[DEBUG] Скрипт: {args.script}")

    if args.script:
        run_script(args.script, process_line)
    else:
        repl()


if __name__ == "__main__":
    main()