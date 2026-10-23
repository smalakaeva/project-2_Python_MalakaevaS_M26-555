"""Главный цикл программы, разбор ввода и вызов команд."""
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import ID_NAME, META_FILE
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    matches,
    select,
    update,
)
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_condition, parse_set, parse_values
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

cache_result = create_cacher()


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, ...) "
          "- создать запись")
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> "
          "- прочитать записи по условию")
    print("<command> update <имя_таблицы> set <столбец> = <значение> "
          "where <столбец> = <значение> - обновить запись")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> "
          "- удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_table(metadata, table_name, rows):
    """Печатает записи таблицы в виде PrettyTable."""
    names = [column.split(":")[0] for column in metadata[table_name]]
    table = PrettyTable()
    table.field_names = names
    for record in rows:
        table.add_row([record[name] for name in names])
    print(table)


def run():
    """Главный цикл: читает команды пользователя и выполняет их."""
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
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
                    result = create_table(metadata, args[1], args[2:])
                    # при ошибке декоратор вернёт None, его сохранять нельзя
                    if result is not None:
                        save_metadata(META_FILE, result)
                        cache_result.clear()
                else:
                    print(f'Некорректное значение: {user_input}. Попробуйте снова.')
            case 'drop_table':
                if len(args) == 2:
                    result = drop_table(metadata, args[1])
                    if result is not None:
                        save_metadata(META_FILE, result)
                        cache_result.clear()
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
                result = insert(metadata, table_name, values, table_data)
                if result is not None:
                    save_table_data(table_name, result)
                    cache_result.clear()
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

                # ключ кэша: таблица + условие
                key = (table_name, str(where))
                rows = cache_result(
                    key,
                    lambda: select(load_table_data(table_name), where),
                )
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
                found = [record for record in table_data if matches(record, where)]
                if not found:
                    print('Записей по такому условию нет.')
                    continue
                ids = ", ".join(str(record[ID_NAME]) for record in found)
                new_data = delete(table_data, where)
                # None - ошибка, та же длина - пользователь ответил "n"
                if new_data is None or len(new_data) == len(table_data):
                    continue
                save_table_data(table_name, new_data)
                cache_result.clear()
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
                found = [record for record in table_data if matches(record, where)]
                if not found:
                    print('Записей по такому условию нет.')
                    continue
                ids = ", ".join(str(record[ID_NAME]) for record in found)
                result = update(table_data, set_clause, where)
                if result is not None:
                    save_table_data(table_name, result)
                    cache_result.clear()
                    print(f'Запись с ID={ids} в таблице "{table_name}" '
                          f'успешно обновлена.')
            case _:
                print(f'Функции {command} нет. Попробуйте снова.')