from datetime import datetime
import json
import os

SPONSORS_FILE = "sponsors.json"

users = {}  
sponsors = set()  
results = []  
active_tests = {}  

def load_sponsors():
    """Загружает спонсоров из файла"""
    global sponsors
    if os.path.exists(SPONSORS_FILE):
        try:
            with open(SPONSORS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                sponsors = set(data)
        except:
            sponsors = set()
    else:
        sponsors = set()
    return sponsors

def save_sponsors():
    """Сохраняет спонсоров в файл"""
    with open(SPONSORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(sponsors), f, ensure_ascii=False, indent=2)

load_sponsors()