import json
import os

DB_FILE = "data.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "orders": []}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user(user_id):
    data = load_data()
    return data["users"].get(str(user_id), {})

def update_user(user_id, new_data):
    data = load_data()
    data["users"][str(user_id)] = new_data
    save_data(data)

def add_order(order):
    data = load_data()
    data["orders"].append(order)
    save_data(data)