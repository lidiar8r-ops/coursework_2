# Настройки БД
import os

# Пути к файлам
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
LOG_DIR = os.path.join(PARENT_DIR, "logs")
DATA_DIR = os.path.join(PARENT_DIR, "data")
# TEMP_DIR = os.path.join(CURRENT_DIR, "tmp")
URL_HH = "https://api.hh.ru/"

filename_areas = os.path.join(DATA_DIR, "areas.json")
filename_vacan = os.path.join(DATA_DIR, "vacancies.json")

