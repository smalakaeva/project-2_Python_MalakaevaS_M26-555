#Этот файл будет отвечать за запуск, игровой цикл и парсинг команд.
import shlex

import prompt

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

DB_FILE = 'db_meta.json'

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
        command = args[0]

        match command:
            case 'create_table':
                if len(args) >= 3:
                    result = create_table(metadata,  args[1] , args[2:])
                    save_metadata(DB_FILE, result)
                else:
                    print('Некорректное значение')
            case 'drop_table':
                if len(args) == 2:
                    result  = drop_table(metadata, args[1] )
                    save_metadata(DB_FILE, result)
                else:
                    print('Некорректное значение')
            case 'help':
                print_help()
            case 'exit':
                break
            case 'list_tables':
                if len(metadata) != 0:
                    for el in metadata.keys():
                        print(f'- {el}')
                else:
                    print('Таблиц нет')
            case _:
                print(f'Функции {command} нет. Попробуйте снова.')

def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

