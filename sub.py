import json
import os

DB_FILE = "database.json"

def _load_data(db_file=DB_FILE):
    if not os.path.exists(db_file):
        return []
    try:
        with open(db_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"Предупреждение: Файл {db_file} не содержит список. Будет создан новый.")
                return []
            return data
    except json.JSONDecodeError:
        print(f"Предупреждение: Файл {db_file} поврежден или не является валидным JSON. Будет создан новый.")
        return []
    except Exception as e:
        print(f"Произошла ошибка при чтении {db_file}: {e}")
        return []

def _save_data(data, db_file=DB_FILE):
    try:
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Произошла ошибка при сохранении в {db_file}: {e}")


def sub(record, db_file=DB_FILE):
    if not isinstance(record, (int, float)):
        print("Ошибка: Запись должна быть числом.")
        return False

    data = _load_data(db_file)
    if record in data:
        print(f"Запись {record} уже существует в базе.")
        return False
    
    data.append(record)
    _save_data(data, db_file)
    print(f"Запись {record} успешно добавлена.")
    return True

def unsub(record, db_file=DB_FILE):
    if not isinstance(record, (int, float)):
        print("Ошибка: Запись для удаления должна быть числом.")
        return False
        
    data = _load_data(db_file)
    if record in data:
        data.remove(record)
        _save_data(data, db_file)
        print(f"Запись {record} успешно удалена.")
        return True
    else:
        print(f"Запись {record} не найдена в базе.")
        return False

def check(record, db_file=DB_FILE):
    if not isinstance(record, (int, float)):
        print("Ошибка: Запись для проверки должна быть числом.")
        return False
        
    data = _load_data(db_file)
    is_present = record in data
    if is_present:
        print(f"Запись {record} найдена в базе.")
    else:
        print(f"Запись {record} не найдена в базе.")
    return is_present