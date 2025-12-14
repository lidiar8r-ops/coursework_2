"""
Модуль для взаимодействия с API HeadHunter (hh.ru).
Позволяет искать вакансии и получать данные о регионах и городах.
"""

# Стандартные библиотеки Python
import json  # Для сериализации и десериализации объектов в формате JSON
import os  # Работа с операционной системой, доступ к файловым операциям

# Внешние зависимости
from typing import Any, Dict, List, Optional  # Типовые подсказки для улучшения качества типов переменных

import requests  # Библиотека для отправки HTTP-запросов (используется для подключения к API hh.ru)

# Внутренние модули проекта
from src import app_logger  # Логгер приложения для журналирования событий
from src.api_hh import BaseAPI  # Базовый класс API для работы с сайтами с вакансиями
from src.config import filename_areas  # Файл конфигурации, содержащий путь к файлу с областями

# Настройка логирования
logger = app_logger.get_logger("api.log")


class AreaAPI(BaseAPI):
    """
    Создание экземпляра класса для работы с API сайтов с вакансиями.

    Этот класс предназначен для извлечения и обработки данных о регионах и городах с использованием API hh.ru.

    Attributes:
        area (str): Название региона или города.
        filename (str): Имя файла для сохранения данных областей.
        session (requests.Session): Сеанс HTTP-запросов.

    Methods:
        get_id_area(): Получает ID области по её названию.
        get_vacancies(name=''): Запрашивает список регионов с сайта hh.ru и сохраняет его в файл.
        find_area_id(data, area_name): Ищет ID области по её названию рекурсивно среди вложенных областей.
        _save_data(data): Сохраняет полученные данные в файл.
    """

    def __init__(self, area: str, filename: str = filename_areas):
        """
        Конструктор класса AreaAPI.

        Args:
            area (str): Название региона или города.
            filename (str, optional): Имя файла для хранения данных областей. По умолчанию берется из config.py.
        """
        self.area = area
        self.filename = filename
        self.session = requests.Session()

    def get_id_area(self) -> str:
        """
        Возвращает ID региона по его названию.

        Сначала проверяется наличие сохраненного файла с областями (`filename`). Если такого файла нет, запрашиваются данные с hh.ru и сохраняются локально.
        Затем выполняется поиск нужного региона по указанному имени.

        Returns:
            str: Идентификатор найденной области либо '0' (если область не найдена).
        """
        # if not os.path.exists(self.filename):
        #     data = self.get_vacancies()
        # else:
        #     with open(self.filename, "r", encoding="utf-8") as f:
        #         data = json.load(f)
        #
        # area_id = self.find_area_id(data, self.area)
        # return area_id

        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Невалидный JSON в файле {self.filename}: {e}")
                data = None
        else:
            data = None

        if data is None:
            # Делаем запрос к API
            data = self._request()
            self._save_data(data)

        return self.find_area_id(data, self.area)

    def get_vacancies(self, name: str = "") -> Optional[Dict[Any, Any]]:
        """
        Запрашивает регионы с сайта hh.ru и возвращает данные в формате JSON.

        Args:
            name (str, optional): Не используется в данном методе, оставлен для совместимости с родительским классом.

        Returns:
            Optional[Dict[Any, Any]]: Данные областей в формате JSON или None в случае ошибок.
        """
        params = {}  # Параметры запроса (пустые, поскольку нам нужны все доступные регионы)
        data = self._request("areas", params)  # Запрос к API hh.ru
        self._save_data(data)  # Сохраняем данные в файл
        return data

    def find_area_id(self, data: Dict, area_name: str) -> int:
        """
        Рекурсивно ищет ID области по её названию среди списка областей.

        Args:
            data (Dict): Структура данных с областями, полученная с hh.ru.
            area_name (str): Название искомого региона или города.

        Returns:
            id: Найденный ID области или 0, если регион не найден.
        """

        areas = data
        if not areas:
            return 0

        def search_in_areas(areas_list, name):
            if not isinstance(areas_list, list):
                return 0  # или raise ValueError

            for area in areas_list:
                if not isinstance(area, dict):
                    continue  # пропускаем не-словари
                if area["name"].strip().lower() == name.strip().lower():
                    return area["id"]
                if "areas" in area and area["areas"]:
                    result = search_in_areas(area["areas"], name)
                    if result:
                        return result
            return 0

        return search_in_areas(areas, area_name)



    def _save_data(self, data):
        """
        Сохраняет переданные данные в указанный файл `filename`.

        Args:
            data: Данные для записи в файл.
        """
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Данные сохранены в {self.filename}")
        except TypeError as e:
            logger.error(f"Объект не сериализуется в JSON: {e}")
        except IOError as e:
            logger.error(f"Ошибка записи в файл {self.filename}: {e}")