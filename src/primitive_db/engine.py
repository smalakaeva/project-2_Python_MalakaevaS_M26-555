# Этот файл будет отвечать за запуск, игровой цикл и парсинг команд.
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.parser import parse_condition, parse_set, parse_values
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

DB_FILE = 'db_meta.json'


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, ...) - создать запись")
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию")
    print("<command> update <имя_таблицы> set <столбец> = <значение> where <столбец> = <значение> - обновить запись")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_table(metadata, table_name, rows):
    names = [column.split(":")[0] for column in metadata[table_name]]
    table = PrettyTable()
    table.field_names = names
    for record in rows:
        table.add_row([record[name] for name in names])
    print(table)


def run():
    print_help()

    while True:
        metadata = load_metadata(DB_FILE)
        user_input = prompt.string('>>>Введите команду: ')
        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f'Некорректное значение: {user_input}. Попробуйте снова.')
            continue
        if not args:
            continue
        command = args[0]

        match command:
            case 'create_table':
                if len(args) >= 3:
                    metadata = create_table(metadata, args[1], args[2:])
                    save_metadata(DB_FILE, metadata)
                else:
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
            case 'drop_table':
                if len(args) == 2:
                    metadata = drop_table(metadata, args[1])
                    save_metadata(DB_FILE, metadata)
                else:
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
            case 'help':
                print_help()
            case 'exit':
                break
            case 'list_tables':
                if metadata:
                    for name in metadata:
                        print(f'- {name}')
                else:
                    print('Таблиц нет')
            case 'info':
                if len(args) != 2:
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
                    continue
                table_name = args[1]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue
                table_data = load_table_data(table_name)
                print(f'Таблица: {table_name}')
                print(f'Столбцы: {", ".join(metadata[table_name])}')
                print(f'Количество записей: {len(table_data)}')
            case 'insert':
                if len(args) < 5 or args[1] != 'into' or args[3] != 'values':
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
                    continue
                table_name = args[2]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue
                values_text = user_input.partition(" values ")[2]
                try:
                    values = parse_values(values_text)
                except ValueError:
                    print(f'Некорректное значение: {values_text}. Попробуйте снова.')
                    continue
                table_data = load_table_data(table_name)
                table_data = insert(metadata, table_name, values, table_data)
                save_table_data(table_name, table_data)
            case 'select':
                if len(args) < 3 or args[1] != 'from':
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
                    continue
                table_name = args[2]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue
                _, sep, where_text = user_input.partition(" where ")
                where = None
                if sep:
                    try:
                        where = parse_condition(where_text)
                    except ValueError:
                        print(f'Некорректное значение: {where_text}. Попробуйте снова.')
                        continue

                table_data = load_table_data(table_name)
                rows = select(table_data, where)
                if not rows:
                    print('Записей нет')
                else:
                    print_table(metadata, table_name, rows)
            case 'delete':
                if len(args) < 3 or args[1] != 'from':
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
                    continue
                table_name = args[2]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                _, sep, where_text = user_input.partition(" where ")
                if not sep:
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
                    continue
                try:
                    where = parse_condition(where_text)
                except ValueError:
                    print(f'Некорректное значение: {where_text}. Попробуйте снова.')
                    continue

                table_data = load_table_data(table_name)
                found = select(table_data, where)
                if not found:
                    print('Записей по такому условию нет.')
                    continue
                ids = ", ".join(str(record["ID"]) for record in found)
                table_data = delete(table_data, where)
                save_table_data(table_name, table_data)
                print(f'Запись с ID={ids} успешно удалена из таблицы "{table_name}".')
            case 'update':
                if len(args) < 4 or args[2] != 'set':
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
                    continue
                table_name = args[1]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                after_set = user_input.partition(" set ")[2]
                set_text, sep, where_text = after_set.partition(" where ")
                if not sep:
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
                    continue
                try:
                    set_clause = parse_set(set_text)
                    where = parse_condition(where_text)
                except ValueError:
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
                    continue

                table_data = load_table_data(table_name)
                found = select(table_data, where)
                if not found:
                    print('Записей по такому условию нет.')
                    continue
                ids = ", ".join(str(record["ID"]) for record in found)
                table_data = update(table_data, set_clause, where)
                save_table_data(table_name, table_data)
                print(f'Запись с ID={ids} в таблице "{table_name}" успешно обновлена.')
            case _:
                print(f'Функции {command} нет. Попробуйте снова.')



