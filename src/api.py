import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from src import app_logger

# Настройка логирования
logger = app_logger.get_logger("api.log")


# # Загрузка переменных из .env-файла
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    def __init_(self, area: str):
        self.area = area


    def get_id_area(self):
        # Если файл area.json существует, то
        # ищем в файле area.json ,
        # если нет получаем файл area.json с hh.ru
        # Далее получаем из area.json id
        pass

    def get_params(self) -> Dict[Any, Any]:
        """Получить параметры для запросов"""
        self.params = base_url = "https://api.hh.ru/areas/"
        super().__init__(base_url)

    def get_areas(self) -> Dict[Any, Any]:
        return self._request("GET", "areas")

    def find_area_id(self, area_name: str) -> str:
        areas = self.get_areas()
        if not areas:
            return None

        def search_in_areas(areas_list, name):
            for area in areas_list:
                if area["name"].strip().lower() == name.strip().lower():
                    return area["id"]
                if "areas" in area and area["areas"]:
                    result = search_in_areas(area["areas"], name)
                    if result:
                        return result
            return None

        return search_in_areas(areas, area_name)
