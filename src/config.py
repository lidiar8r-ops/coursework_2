# Настройки БД
import os

# Пути к файлам
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
LOG_DIR = os.path.join(PARENT_DIR, "logs")
DATA_DIR = os.path.join(PARENT_DIR, "data")
# TEMP_DIR = os.path.join(CURRENT_DIR, "tmp")
URL_HH = "https://api.hh.ru/"

# определим список с именем обрабатываемого файла (operations.xlsx) и его поля
LIST_OPERATION = [
    # "operations.csv",
    "operations.xlsx",
    [
        "Дата операции",
        "Дата платежа",
        "Номер карты",
        "Статус",
        "Сумма операции",
        "Валюта операции",
        "Сумма платежа",
        "Валюта платежа",
        "Кэшбэк",
        "Категория",
        "MCC",
        "Описание",
        "Бонусы (включая кэшбэк)",
        "Округление на инвесткопилку",
        "Сумма операции с округлением",
    ],
    "Валюта платежа",
    "Сумма платежа",
    "Категория",
]

# URL_EXCHANGE = "https://api.apilayer.com/exchangerates_data/convert"
URL_EXCHANGE = "https://v6.exchangerate-api.com/v6/"
# URL_EXCHANGE_SP_500 = "https://www.alphavantage.co"
URL_EXCHANGE_SP_500 = "https://financialmodelingprep.com/stable/stock-peers?"
# URL_EXCHANGE_SP_500 = "https://financialmodelingprep.com/api/v3/quote-short/{','.join(symbols)}?apikey={api_key}""

#
# DATABASE_URL = "sqlite:///app.db"
# MAX_CONNECTIONS = 10
#
# # Логирование
# LOG_LEVEL = "DEBUG"
# # LOG_FILE = "app.log"
#
# # # Функциональные флаги
# # DEBUG = True
# # ENABLE_CACHING = False
