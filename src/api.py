import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from src import app_logger

# Настройка логирования
logger = app_logger.get_logger("api.log")


# # Загрузка переменных из .env-файла
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAPI(ABC):
    """Абстрактный базовый класс для работы с API"""

    def __init__(self, base_url: str):
        self.base_url = base_url


    @abstractmethod
    def get_params(self) -> Dict[Any, Any]:
        """Получить параметры для запросов"""
        pass

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Вспомогательный метод для выполнения HTTP-запросов"""
        url = f"{self.base_url}/{endpoint}"

        try:
            response = self.session.request(method, url, **kwargs)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                logger.error(f"Необходимо пройти CAPTCHA для : {url}")
                return None
            elif response.status_code == 404:
                logger.error(f"Указанная вакансия не существует или у пользователя нет прав для просмотра вакансии:"
                                  f" {url}")
                return None
            elif response.status_code == 401:
                logger.error("Неавторизованный запрос. Проверьте токен.")
                return None
            elif response.status_code == 429:
                logger.error("Слишком много запросов запросов к API.")
                return None
            else:
                logger.error(
                    f"Ошибка {response.status_code}: {response.text}"
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети: {e}")
            return None


# class ConnAPI(BaseAPI):
#     """ класс, наследующийся от абстрактного класса, для работы с платформой hh.ru.
#     Класс умеет подключаться к API и получать вакансии."""
#


class HeadHunterAPI(BaseAPI):
    """ класс, наследующийся от абстрактного класса, для работы с платформой hh.ru.
        Класс умеет подключаться к API и получать вакансии. """

    def __init_(self):
        pass

    def get_params(self, id: int = 104) -> Dict[Any, Any]:
        """Получить параметры для запросов"""
        self.params = {
            "text": name,
            "area": id,  # Челябинск (по умолчанию, пока что)
            "per_page": 20,  # количество вакансий в ответе
            "page": 0  # страница результатов
        }

    def get_vacancies(self,  query: str, area: str = None) -> Dict[Any, Any]:
        """Получение вакансий с hh.ru в формате JSON
           Args:
               query (str): поисковый запрос (название вакансии, навык и т.п.)
           Returns:
               dict: JSON-ответ от API hh.ru
        """
        pass


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

   #
# import requests
#
# url_get = "https://httpbin.org/get" # используемый адрес для отправки запроса
#
# response = requests.get(url_get) # отправка GET-запроса
#
# print(response) # вывод объекта класса Response
# # Вывод:
# >> <Response [200]>
#
# print(response.status_code) # вывод статуса запроса, 200 означает, что всё хорошо, остальные коды нас пока не интересуют и их можно считать показателем ошибки
# # Вывод:
# >> 200
#
# print(response.text) # печать ответа в виде текста того, что вернул нам внешний сервис
# # Вывод:
# >> {
# >>   "args": {},
# >>   "headers": {
# >>     "Accept": "*/*",
# >>     "Accept-Encoding": "gzip, deflate",
# >>     "Host": "httpbin.org",
# >>     "User-Agent": "python-requests/2.31.0",
# >>     "X-Amzn-Trace-Id": "Root=1-65892ff5-5f3e46891d0c56775f3dc659"
# >>   },
# >>   "origin": "185.252.41.5",
# >>   "url": "https://httpbin.org/get"
# >> }
#
# print(response.json()) # печать ответа в виде json-объекта того, что нам вернул внешний сервис
# # Вывод:
# >> {'args': {}, 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'Host': 'httpbin.org', 'User-Agent': 'python-requests/2.31.0', 'X-Amzn-Trace-Id': 'Root=1-65892ff5-5f3e46891d0c56775f3dc659'}, 'origin': '185.252.41.5', 'url': 'https://httpbin.org/get'}

# Работа с POST-запросами:
#
# import requests
#
# url_post = "https://httpbin.org/post" # используемый адрес для отправки запроса
#
# response = requests.post(url_post) # отправка POST-запроса
#
# print(response) # вывод объекта класса Response
# # Вывод:
# >> <Response [200]>
#
# print(response.status_code) # вывод статуса запроса, 200 означает, что всё хорошо
# # Вывод:
# >> 200
#
# print(response.text) # печать ответа в виде текста того, что вернул нам внешний сервис
# # Вывод:
# >> {
# >>   "args": {},
# >>   "data": "",
# >>   "files": {},
# >>   "form": {},
# >>   "headers": {
# >>     "Accept": "*/*",
# >>     "Accept-Encoding": "gzip, deflate",
# >>     "Content-Length": "0",
# >>     "Host": "httpbin.org",
# >>     "User-Agent": "python-requests/2.31.0",
# >>     "X-Amzn-Trace-Id": "Root=1-65893054-044490af734f11d751ff9f85"
# >>   },
# >>   "json": null,
# >>   "origin": "185.252.41.5",
# >>   "url": "https://httpbin.org/post"
# >> }
#
# print(response.json()) # печать ответа в виде json объекта того, что нам вернул внешний сервис
# # Вывод:
# >>{'args': {}, 'data': '', 'files': {}, 'form': {}, 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'Content-Length': '0', 'Host': 'httpbin.org', 'User-Agent': 'python-requests/2.31.0', 'X-Amzn-Trace-Id': 'Root=1-65893054-044490af734f11d751ff9f85'}, 'json': None, 'origin': '185.252.41.5', 'url': 'https://httpbin.org/post'}
#
