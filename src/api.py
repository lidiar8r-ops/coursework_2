import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List

import requests

from src import app_logger
from src.api_hh import BaseAPI
from src.config import filename_areas

# Настройка логирования
logger = app_logger.get_logger("api.log")

# class AreaAPI(BaseAPI):
#     """ класс, наследующийся от абстрактного класса, для работы с платформой hh.ru.
#         Класс умеет подключаться к API и получать вакансии. """
#
#     def __init_(self):
#         pass
#
#     def get_params(self, id: int = 104) -> Dict[Any, Any]:
#         """Получить параметры для запросов"""
#         self.params = {
#             "text": name,
#             "area": id,  # Челябинск (по умолчанию, пока что)
#             "per_page": 20,  # количество вакансий в ответе
#             "page": 0  # страница результатов
#         }
#
#     def get_vacancies(self,  query: str, area: str = None) -> Dict[Any, Any]:
#         """Получение вакансий с hh.ru в формате JSON
#            Args:
#                query (str): поисковый запрос (название вакансии, навык и т.п.)
#            Returns:
#                dict: JSON-ответ от API hh.ru
#         """
#         pass


class AreaAPI(BaseAPI):
    """Создание экземпляра класса для работы с API сайтов с вакансиями"""
    def __init__(self, area: str, filename: str = filename_areas):
        self.area = area
        self.filename = filename
        self.session = requests.Session()


    def get_id_area(self):
        # Если файл area.json существует, то
        # ищем в файле area.json ,
        # если нет получаем файл area.json с hh.ru
        # Далее получаем из area.json id
        if not os.path.exists(self.filename):
            data = self.get_vacancies()
        else:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)

        area_id =  self.find_area_id(data, self.area)
        return area_id


    def get_vacancies(self, name: str = "") -> List[Dict[str, Any]]:
        # params = {"name": name}
        params = {}
        data = self._request("areas", params)  # вызов внутри класса
        self._save_data(data)
        return data


    def find_area_id(self, data: dict, area_name: str) -> str:
        areas = data
        if not areas:
            return 0

        def search_in_areas(areas_list, name):
            for area in areas_list:
                if area["name"].strip().lower() == name.strip().lower():
                    return area["id"]
                if "areas" in area and area["areas"]:
                    result = search_in_areas(area["areas"], name)
                    if result:
                        return result
            return 0

        return search_in_areas(areas, area_name)


    def _save_data(self, data):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data,
                    f,
                    ensure_ascii=False,
                    indent=4
                )
        except IOError as e:
            logger.error(f"Ошибка при сохранении в файл {self.filename}: {e}")