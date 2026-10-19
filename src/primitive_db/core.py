from primitive_db.utils import save_metadata, load_metadata

#Здесь будет основная логика работы с таблицами и данными.
def create_table(metadata, table_name, columns):
    types = ['int', 'str', 'bool']

    if table_name in metadata.keys():
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    for col in columns:
        parts = col.split(':')
        if  len(parts) != 2:
            print(f'Ошибка формата. Попробуйте снова.')
            return metadata
        if col.split(':')[1] not in types:
            print(f'Некорректный тип данных. Попробуйте снова.')
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




