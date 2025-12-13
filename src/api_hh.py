import requests
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from src import app_logger

# Настройка логирования
logger = app_logger.get_logger("api.log")


# АБСТРАКТНЫЙ КЛАСС ДЛЯ РАБОТЫ С API
class VacancyAPI(ABC):
    @abstractmethod
    def get_vacancies(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Получить вакансии по поисковому запросу"""
        pass

# КЛАСС ДЛЯ РАБОТЫ С HH.RU API
class HeadHunterAPI(VacancyAPI):
    BASE_URL = "https://api.hh.ru/vacancies"

    def __init__(self):
        self.session = requests.Session()

    def get_vacancies(self, query: str, area: int = 104, per_page: int = 20) -> List[Dict[str, Any]]:
        params = {
            "text": query,
            "area": area,
            "per_page": per_page,
            "page": 0
        }
        try:
            response = self.session.get(self.BASE_URL, params=params)

            if response.status_code == 200:
                return response.json().get("items", [])
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