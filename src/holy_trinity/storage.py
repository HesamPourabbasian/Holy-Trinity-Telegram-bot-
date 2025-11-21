import json
import os

DATA_FILE = "../../tests/tasks.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    migrated_data, changed = migrate_old_format(data)
    if changed:
        save_data(migrated_data)

    return migrated_data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def migrate_old_format(data):
    changed = False
    for user_id in data:
        for date in data[user_id]:
            new_list = []
            for item in data[user_id][date]:
                if isinstance(item, str):
                    new_list.append({"task": item, "done": False})
                    changed = True
                else:
                    new_list.append(item)
            data[user_id][date] = new_list
    return data, changed
