import json
import os


def load_metadata(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            dic = json.load(f)
            return dic
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        # indent=4 каждая вложенность на новой строке с отступом.
        # ensure_ascii=False оставляет русские буквы как есть
        json.dump(data, f, indent=4, ensure_ascii=False)



def load_table_data(table_name):
    try:
        file = os.path.join('data', f'{table_name}.json')
        with open(file, 'r', encoding='utf-8') as f:
            dic = json.load(f)
            return dic
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    os.makedirs("data", exist_ok=True)
    with open(os.path.join('data', f'{table_name}.json'), 'w', encoding='utf-8') as f:
        # indent=4 каждая вложенность на новой строке с отступом.
        # ensure_ascii=False оставляет русские буквы как есть
        json.dump(data, f, indent=4, ensure_ascii=False)

