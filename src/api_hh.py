import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

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

    def __init__(self) -> None:
        """Инициализирует HTTP‑сессию для запросов к API."""
        self.session: requests.Session = requests.Session()

    @abstractmethod  # pragma: no cover
    def get_requests(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Абстрактный метод для получения данных по заданному поисковому запросу.

        Args:
            query (str): Основное ключевое слово или фраза для поиска вакансий.
            **kwargs (Any): Дополнительные аргументы для фильтрации результата
                (например, регион поиска, зарплата, опыт).

        Returns:
            List[Dict[str, Any]]: Список вакансий в формате JSON-дикт. Каждый элемент
                содержит поля, специфичные для источника данных.
        """
        pass

    def _request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Выполняет HTTP-запросы к API сервиса.

        Args:
            endpoint (str): Часть URL (например, 'vacancies').
            params (Dict[str, Any]): Параметры запроса.

        Returns:
            Optional[Dict[str, Any]]: JSON-ответ или None при ошибке.
        """
        self.url = f"{URL_HH}/{endpoint}"
        try:
            response = self.session.get(self.url, params=params)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    return data
                logger.error("Ответ API не является словарём")
                return None

            # Обработка ошибок HTTP
            if response.status_code == 403:
                logger.error(f"Необходимо пройти CAPTCHA: {self.url}")
            elif response.status_code == 404:
                logger.error(f"Ресурс не найден: {self.url}")
            elif response.status_code == 401:
                logger.error("Неавторизованный запрос. Проверьте токен.")
            elif response.status_code == 429:
                logger.error("Превышен лимит запросов к API.")
            else:
                logger.error(f"HTTP {response.status_code}: {response.text}")

            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети: {e}")
            return None
        except json.JSONDecodeError:
            logger.error("Не удалось декодировать JSON")
            return None


class HeadHunterAPI(BaseAPI):
    """
    Специализированный класс для работы с API HeadHunter (hh.ru).

    Основные методы:
        get_vacancies(query: str, excluded_text: str, area: int = 104, per_page: int = 20) -> List[Dict[str, Any]]
            Получает список вакансий по запросу с возможностью исключения определенных ключевых слов.
    """

    def __init__(self) -> None:
        """
        Конструктор класса, создает сессию для HTTP-запросов.
        """
        self.session = requests.Session()

    def _parse_items(self, data: Any) -> List[Dict[str, Any]]:
        """Безопасно извлекает items из ответа API."""
        if not isinstance(data, dict):
            return []

        items = data.get("items", [])
        if isinstance(items, list) and all(isinstance(item, dict) for item in items):
            return items
        return []

    def get_requests(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
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
        params = {
            "text": query,
            "excluded_text": kwargs.get("excluded_text", ""),
            "area": kwargs.get("area", 104),
            "per_page": kwargs.get("per_page", 20),
        }

        all_vacancies = []
        page = 0

        while True:
            params["page"] = page
            data = self._request("vacancies", params)

            # Если запрос не удался или нет данных — выходим
            if not data:
                break

            items = self._parse_items(data)
            # Если на текущей странице нет вакансий — выходим (конец пагинации)
            if not items:
                break

            all_vacancies.extend(items)

            # Проверяем, есть ли ещё страницы
            total_pages = data.get("pages", 0)
            # Выходим, если:
            # - достигли последней страницы (page >= total_pages - 1)
            # - собрали достаточно вакансий (len(all_vacancies) >= per_page)
            if page >= total_pages - 1 or len(all_vacancies) >= kwargs.get("per_page", 20):
                break

            page += 1

        # Возвращаем не больше per_page вакансий
        return all_vacancies[: kwargs.get("per_page", 20)]

    def _request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Выполняет HTTP-запросы к API сервиса.
        """
        return super()._request(endpoint, params)
