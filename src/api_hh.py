from abc import ABC, abstractmethod
from typing import Any, Dict, List

import requests

from src import app_logger
from src.config import URL_HH

# Настройка логирования
logger = app_logger.get_logger("api_hh.log")


class BaseAPI(ABC):
    """АБСТРАКТНЫЙ КЛАСС ДЛЯ РАБОТЫ С API"""

    @abstractmethod
    def get_vacancies(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Получить данные по поисковому запросу"""
        pass

    def _request(self, endpoint: str, params: dict) -> Dict[Any, Any]:
        """Вспомогательный метод для выполнения HTTP-запросов"""
        self.url = f"{URL_HH}/{endpoint}"
        try:
            response = self.session.get(self.url, params=params)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                logger.error(f"Необходимо пройти CAPTCHA для : {self.url}")
                return None
            elif response.status_code == 404:
                logger.error(
                    f"Указанная вакансия не существует или у пользователя нет прав для просмотра вакансии:"
                    f" {self.url}"
                )
                return None
            elif response.status_code == 401:
                logger.error("Неавторизованный запрос. Проверьте токен.")
                return None
            elif response.status_code == 429:
                logger.error("Слишком много запросов запросов к API.")
                return None
            else:
                logger.error(f"Ошибка {response.status_code}: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети: {e}")
            return None


class HeadHunterAPI(BaseAPI):
    # КЛАСС ДЛЯ РАБОТЫ С HH.RU API
    def __init__(self):
        self.session = requests.Session()

    def get_vacancies(
        self, query: str, excluded_text: str, area: int = 104, per_page: int = 20
    ) -> List[Dict[str, Any]]:
        params = {"text": query, "excluded_text": excluded_text, "area": area, "per_page": per_page, "page": 0}
        data = self._request("vacancies", params)
        # Проверяем, что data не None и это словарь
        if not data or not isinstance(data, dict):
            logger.warning("Получен пустой или невалидный ответ от API: %s", data)
            return []

        data_query = data.get("items", [])
        return data_query