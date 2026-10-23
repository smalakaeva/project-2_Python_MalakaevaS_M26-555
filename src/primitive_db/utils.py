"""Вспомогательные функции для чтения и записи JSON-файлов."""
import json
import os

from primitive_db.constants import DATA_DIR


def load_metadata(filepath):
    """Загружает метаданные таблиц из файла, если файла нет - пустой словарь."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            dic = json.load(f)
            return dic
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные таблиц в файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        # indent=4 каждая вложенность на новой строке с отступом.
        # ensure_ascii=False оставляет русские буквы как есть
        json.dump(data, f, indent=4, ensure_ascii=False)


def table_path(table_name):
    """Возвращает путь к файлу с записями таблицы."""
    return os.path.join(DATA_DIR, f'{table_name}.json')


def load_table_data(table_name):
    """Загружает записи таблицы, если файла нет - пустой список."""
    try:
        with open(table_path(table_name), 'r', encoding='utf-8') as f:
            dic = json.load(f)
            return dic
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в файл."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(table_path(table_name), 'w', encoding='utf-8') as f:
        # indent=4 каждая вложенность на новой строке с отступом.
        # ensure_ascii=False оставляет русские буквы как есть
        json.dump(data, f, indent=4, ensure_ascii=False)
