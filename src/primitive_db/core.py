"""Логика работы с таблицами и записями."""
from primitive_db.constants import ID_NAME, ID_TYPE, VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу и возвращает обновлённые метаданные."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    for col in columns:
        parts = col.split(':')
        if len(parts) != 2:
            print('Ошибка формата. Попробуйте снова.')
            return metadata
        if parts[1] not in VALID_TYPES:
            print('Некорректный тип данных. Попробуйте снова.')
            return metadata

    columns = [f'{ID_NAME}:{ID_TYPE}'] + columns
    metadata[table_name] = columns
    print(f'Таблица "{table_name}" успешно создана со столбцами: {", ".join(columns)}')
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу и возвращает обновлённые метаданные."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    metadata.pop(table_name, None)
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    """Добавляет запись в таблицу и возвращает обновлённые данные."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data
    schema = metadata[table_name]

    if len(values) != len(schema) - 1:
        print(f'Ошибка: количество значений не соответствует количеству '
              f'столбцов в таблице "{table_name}".')
        return table_data

    record = {}
    for column, value in zip(schema[1:], values):
        name, type_name = column.split(":")

        ok = isinstance(value, VALID_TYPES[type_name])
        if type_name == "int" and isinstance(value, bool):
            ok = False

        if not ok:
            print(f'Некорректное значение: {value}. Попробуйте снова.')
            return table_data

        record[name] = value

    ids = [row[ID_NAME] for row in table_data]
    new_id = max(ids, default=0) + 1

    full_record = {ID_NAME: new_id, **record}
    table_data.append(full_record)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def matches(record, where_clause):
    """Проверяет, подходит ли запись под условие where."""
    return all(record.get(key) == value for key, value in where_clause.items())


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает все записи или только подходящие под условие where."""
    if where_clause is None:
        return table_data

    result = []
    for record in table_data:
        if matches(record, where_clause):
            result.append(record)
    return result


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет записи, подходящие под условие where."""
    for record in table_data:
        if matches(record, where_clause):
            record.update(set_clause)
    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    """Удаляет записи, подходящие под условие where."""
    result = []
    for record in table_data:
        if not matches(record, where_clause):
            result.append(record)
    return result







