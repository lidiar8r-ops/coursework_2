from abc import ABC, abstractmethod
from typing import Any, Dict, List

import requests

from src import app_logger
from src.config import URL_HH

# Настройка логирования
logger = app_logger.get_logger("api_hh.log")


class BaseAPI(ABC):
    """
    Абстрактный базовый класс для работы с API-сервисами вакансий.

    Атрибуты:
        Нет (абстрактный класс не предполагает хранение состояния).

    Методы:
        get_vacancies(query: str, **kwargs) -> List[Dict[str, Any]]:
            Абстрактный метод для получения списка вакансий по заданному запросу.

        _request(endpoint: str, params: dict) -> Dict[Any, Any]:
            Обеспечивает выполнение HTTP-запросов к API.
    """

    @abstractmethod
    def get_vacancies(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Абстрактный метод для получения списка вакансий по заданному поисковому запросу.

        Args:
            query (str): Основное ключевое слово или фраза для поиска вакансий.
            **kwargs: Дополнительные аргументы для фильтрации результата (например, регион поиска).

        Returns:
            List[Dict[str, Any]]: Список вакансий в формате JSON-дикт.
        """
        pass

    def _request(self, endpoint: str, params: dict) -> Dict[Any, Any]:
        """
        Выполняет HTTP-запросы к API сервиса.

        Args:
            endpoint (str): Часть URL, определяющая точку доступа к данным (например, 'vacancies').
            params (dict): Словарь параметров для передачи в запросе.

        Returns:
            Dict[Any, Any]: JSON-ответ от API.
        """
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
                    f"Указанная вакансия не существует или у пользователя нет прав для просмотра вакансии: {self.url}"
                )
                return None
            elif response.status_code == 401:
                logger.error("Неавторизованный запрос. Проверьте токен.")
                return None
            elif response.status_code == 429:
                logger.error("Слишком много запросов к API.")
                return None
            else:
                logger.error(f"Ошибка {response.status_code}: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети: {e}")
            return None


class HeadHunterAPI(BaseAPI):
    """
    Специализированный класс для работы с API HeadHunter (hh.ru).

    Основные методы:
        get_vacancies(query: str, excluded_text: str, area: int = 104, per_page: int = 20) -> List[Dict[str, Any]]
            Получает список вакансий по запросу с возможностью исключения определенных ключевых слов.
    """

    def __init__(self):
        """
        Конструктор класса, создает сессию для HTTP-запросов.
        """
        self.session = requests.Session()

    def get_vacancies(
        self, query: str, excluded_text: str, area: int = 104, per_page: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Получает список вакансий по заданному запросу с фильтрацией и ограничением количества записей.

        Args:
            query (str): Основная строка для поиска вакансий.
            excluded_text (str): Исключение текста (например, удаленные ключевые слова).
            area (int, optional): Код региона (по умолчанию — Челябинская область).
            per_page (int, optional): Максимальное число вакансий на странице (по умолчанию — 20).

        Returns:
            List[Dict[str, Any]]: Список вакансий в формате JSON.
        """
        params = {"text": query, "excluded_text": excluded_text, "area": area, "per_page": per_page, "page": 0}
        data = self._request("vacancies", params)
        # Проверяем валидность полученных данных
        if not data or not isinstance(data, dict):
            logger.warning("Получен пустой или невалидный ответ от API: %s", data)
            return []

        data_query = data.get("items", [])
        return data_query
