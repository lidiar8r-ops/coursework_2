"""
Модуль для взаимодействия с API HeadHunter (hh.ru).
Позволяет искать вакансии и получать данные о регионах и городах.
"""

# Стандартные библиотеки Python
import json  # Для сериализации и десериализации объектов в формате JSON
import os  # Работа с операционной системой, доступ к файловым операциям

# Внешние зависимости
from typing import Any, Dict, List, Union  # Типовые подсказки для улучшения качества типов переменных

import requests  # Библиотека для отправки HTTP-запросов (используется для подключения к API hh.ru)

# Внутренние модули проекта
from src import app_logger  # Логгер приложения для журналирования событий
from src.api_hh import BaseAPI  # Базовый класс API для работы с сайтами с вакансиями
from src.config import filename_areas  # Файл конфигурации, содержащий путь к файлу с областями

# Настройка логирования
logger = app_logger.get_logger("area.log")


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
        get_request(name=''): Запрашивает список регионов с сайта hh.ru и сохраняет его в файл.
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
        Сначала проверяется наличие сохраненного файла с областями (`filename`). Если такого файла нет, запрашиваются
        данные с hh.ru и сохраняются локально.
        Затем выполняется поиск нужного региона по указанному имени.
        Returns:
            str: Идентификатор найденной области либо '0' (если область не найдена).
        """
        if not os.path.exists(self.filename):
            try:
                data = self.get_requests("")
                if data is None:
                    return "0"
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка при запросе к API: {e}")
                return "0"
            except Exception as e:
                logger.error(f"Неожиданная ошибка при запросе к API: {e}")
                return "0"
        else:
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Ошибка при чтении файла {self.filename}: {e}")
                return "0"

        area_id = self.find_area_id(data, self.area)

        # Явная проверка и преобразование типа
        if isinstance(area_id, str):
            return area_id
        elif area_id is None:
            return "0"
        else:
            # Если area_id не строка (например, int), преобразуем
            return str(area_id)

    def get_requests(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Получает данные по поисковому запросу.

        Args:
            query (str): Поисковый запрос.
            **kwargs (Any): Дополнительные параметры API (не используются в текущей реализации).

        Returns:
            List[Dict[str, Any]]: Список данных в формате API.
        """
        try:
            # Запрос к API для получения регионов (как в вашей текущей логике)
            params: Dict[str, Any] = {}
            data = self._request("areas", params)
            self._save_data(data)

            # Преобразуем ответ в требуемый формат (список словарей)
            if isinstance(data, dict):
                return [data]  # Обернуть словарь в список
            elif isinstance(data, list):
                return data
            else:
                logger.warning("Некорректный формат ответа API: %s", data)
                return []

        except Exception as e:
            logger.error("Ошибка при запросе данных: %s", e)
            return []

    # def find_area_id(self, data: List[Dict[str, Any]], area_name: str) -> str:
    def find_area_id(
        self, data: Union[List[Dict[str, Any]], Dict[str, Any]], target_name: str  # список или словарь
    ) -> str:
        """
        Рекурсивно ищет ID области по её названию среди списка областей.

        Args:
            data: Список словарей с данными о регионах. Каждый словарь может содержать:
                - "name": название региона (str)
                - "id": идентификатор региона (int/str)
                - "areas": вложенные регионы (list of dict)
            area_name: Название искомого региона или города.

        Returns:
            str: Найденный ID региона в виде строки или "0", если регион не найден.
        """
        # if not data:
        #     return "0"
        #
        # target_name = area_name.strip().lower()
        #
        # def search_in_areas(areas: List[Dict[str, Any]]) -> str:
        #     for area in areas:
        #         # 1. Проверяем имя текущего региона
        #         current_name = area.get("name", "").strip().lower()
        #         if current_name == target_name:
        #             area_id = area.get("id")
        #             return str(area_id) if area_id is not None else "0"
        #
        #         # 2. Проверяем вложенные регионы
        #         sub_areas = area.get("areas")
        #         if isinstance(sub_areas, list) and sub_areas:
        #             result = search_in_areas(sub_areas)
        #             if result != "0":
        #                 return result
        #     return "0"
        #
        # return search_in_areas(data)
        target_name = target_name.strip().lower()

        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            logger.warning("Некорректный тип данных: %s", type(data))
            return "0"

        def search_in_areas(areas: List[Dict[str, Any]]) -> str:
            for area in areas:
                current_name = area.get("name", "").strip().lower()
                if current_name == target_name:
                    # Явно приводим к str
                    return str(area.get("id", "0"))
                if "areas" in area:
                    result = search_in_areas(area["areas"])
                    if result != "0":
                        return result
            return "0"

        return search_in_areas(data)

    def _save_data(self, data: Any) -> None:
        """
        Сохраняет переданные данные в указанный файл `self.filename` в формате JSON.

        Args:
            data (Any): Данные для записи в файл. Должны быть сериализуемы в JSON
                (например: dict, list, str, int, bool, None).

        Raises:
            IOError: Если произошла ошибка при работе с файлом (нет прав, диск полон и т.п.).
        Returns:
            None: Метод не возвращает значение, только выполняет запись в файл.
        """
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            logger.error(f"Ошибка при сохранении в файл {self.filename}: {e}")
            raise
