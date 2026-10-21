TYPES = {"int": int, "str": str, "bool": bool}
def create_table(metadata, table_name, columns):
    types = ['int', 'str', 'bool']

    if table_name in metadata.keys():
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    for col in columns:
        parts = col.split(':')
        if  len(parts) != 2:
            print('Ошибка формата. Попробуйте снова.')
            return metadata
        if col.split(':')[1] not in types:
            print('Некорректный тип данных. Попробуйте снова.')
            return metadata

    columns = ["ID:int"] + columns
    metadata[table_name] = columns
    print(f'Таблица "{table_name}" успешно создана со столбцами: {", ".join(columns)}')
    return metadata

def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    metadata.pop(table_name, None)
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def insert(metadata, table_name, values, table_data):

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

        ok = isinstance(value, TYPES[type_name])
        if type_name == "int" and isinstance(value, bool):
            ok = False

        if not ok:
            print(f'Некорректное значение: {value}. Попробуйте снова.')
            return table_data

        record[name] = value

    ids = [row["ID"] for row in table_data]
    new_id = max(ids, default=0) + 1

    full_record = {"ID": new_id, **record}
    table_data.append(full_record)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data

def matches(record, where_clause):
    return all(record.get(key) == value for key, value in where_clause.items())

def select(table_data, where_clause=None):
    if where_clause is None:
        return table_data
    else:
        result = []
        for record in table_data:
            if matches(record, where_clause):
                result.append(record)
        return (result)


def update(table_data, set_clause, where_clause):
    for record in table_data:
        if matches(record, where_clause):
            record.update(set_clause)
    return table_data


def delete(table_data, where_clause):
    res = []
    for record in table_data:
        if not (matches(record, where_clause)):
            res.append(record)
    return res







