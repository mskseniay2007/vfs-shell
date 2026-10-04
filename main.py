"""VFS Shell — эмулятор командной строки UNIX-подобной ОС.

Этап 4: реализованы команды uname и uniq.
"""

import argparse
import json


# ---------- Работа с VFS ----------

def load_vfs(path):
    """Загружает VFS из JSON-файла в память."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_child(node, name):
    """Ищет дочерний узел с заданным именем."""
    for child in node.get("children", []):
        if child["name"] == name:
            return child
    return None


def get_node(root, path_list):
    """Возвращает узел по списку имён от корня."""
    current = root
    for name in path_list:
        current = find_child(current, name)
        if current is None:
            return None
    return current


def resolve_path(root, cwd, target):
    """
    Превращает target (путь от cwd) в список имён от корня.
    Возвращает список или None, если путь некорректен.
    """
    if target.startswith("/"):
        new_path = []
        parts = [p for p in target.split("/") if p]
    else:
        new_path = list(cwd)
        parts = [p for p in target.split("/") if p]

    for part in parts:
        if part == ".":
            continue
        if part == "..":
            if new_path:
                new_path.pop()
            continue
        current_node = get_node(root, new_path)
        child = find_child(current_node, part)
        if child is None or child["type"] != "dir":
            return None
        new_path.append(part)
    return new_path


def path_to_str(path_list):
    """Превращает список имён в строку вида /home/user."""
    if not path_list:
        return "/"
    return "/" + "/".join(path_list)


# ---------- Команды ----------

def cmd_ls(root, cwd, args):
    """Выводит содержимое каталога."""
    target = cwd
    if args:
        new_path = resolve_path(root, cwd, args[0])
        if new_path is None:
            print(f"ls: {args[0]}: нет такого файла или каталога")
            return
        target = new_path

    node = get_node(root, target)
    if node is None or node["type"] != "dir":
        print("ls: не каталог")
        return

    children = node.get("children", [])
    if not children:
        return
    for child in children:
        suffix = "/" if child["type"] == "dir" else ""
        print(child["name"] + suffix)


def cmd_cd(root, cwd, args):
    """Меняет текущий каталог. Возвращает новый cwd."""
    if not args:
        return []
    new_path = resolve_path(root, cwd, args[0])
    if new_path is None:
        print(f"cd: {args[0]}: нет такого каталога")
        return cwd
    return new_path


def cmd_uname(args):
    """Печатает имя системы."""
    print("VFS-Shell 1.0")


def cmd_uniq(root, cwd, args):
    """Читает файл из VFS и удаляет подряд идущие одинаковые строки."""
    if not args:
        print("uniq: укажите имя файла")
        return

    target = args[0]
    if target.startswith("/"):
        path_list = [p for p in target.split("/") if p]
    else:
        path_list = list(cwd) + [p for p in target.split("/") if p]

    node = get_node(root, path_list)
    if node is None:
        print(f"uniq: {target}: нет такого файла")
        return
    if node["type"] != "file":
        print(f"uniq: {target}: это каталог")
        return

    content = node.get("content", "")
    previous = None
    for line in content.splitlines():
        if line != previous:
            print(line)
        previous = line


# ---------- Обработка команд ----------

def parse_command(line):
    """Разбивает строку на команду и аргументы."""
    parts = line.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]


def process_line(line, state):
    """
    Обрабатывает строку. state — словарь с root и cwd.
    Возвращает False, если нужно выйти.
    """
    cmd, args = parse_command(line)
    if cmd is None:
        return True

    if cmd == "exit":
        print("Выход.")
        return False
    elif cmd == "ls":
        cmd_ls(state["root"], state["cwd"], args)
    elif cmd == "cd":
        state["cwd"] = cmd_cd(state["root"], state["cwd"], args)
    elif cmd == "uname":
        cmd_uname(args)
    elif cmd == "uniq":
        cmd_uniq(state["root"], state["cwd"], args)
    else:
        print(f"{cmd}: команда не найдена")
    return True


# ---------- Запуск ----------

def parse_args():
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(description="Эмулятор shell с VFS")
    parser.add_argument("--vfs", required=True, help="Путь к JSON-файлу VFS")
    parser.add_argument("--script", help="Путь к стартовому скрипту")
    return parser.parse_args()


def print_motd(root):
    """Печатает motd из корня VFS, если он есть."""
    motd = find_child(root, "motd")
    if motd and motd["type"] == "file":
        print(motd.get("content", ""))


def run_script(path, state):
    """Выполняет команды из файла-скрипта."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")
                if not line.strip():
                    continue
                if line.lstrip().startswith("#"):
                    continue
                print(f"user@vfs:{path_to_str(state['cwd'])}$ {line}")
                if not process_line(line, state):
                    break
    except FileNotFoundError:
        print(f"Ошибка: файл скрипта '{path}' не найден.")
    except Exception as e:
        print(f"Ошибка при выполнении скрипта: {e}")


def repl(state):
    """Главный цикл интерактивного режима."""
    print("VFS Shell v0.1 (этап 4). Введите 'exit' для выхода.")
    while True:
        try:
            line = input(f"user@vfs:{path_to_str(state['cwd'])}$ ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not process_line(line, state):
            break


def main():
    """Точка входа."""
    args = parse_args()

    print(f"[DEBUG] VFS: {args.vfs}")
    print(f"[DEBUG] Скрипт: {args.script}")

    root = load_vfs(args.vfs)
    state = {"root": root, "cwd": []}

    print_motd(root)

    if args.script:
        run_script(args.script, state)
    else:
        repl(state)


if __name__ == "__main__":
    main()