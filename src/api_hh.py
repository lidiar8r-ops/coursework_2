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
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к API: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
            return []
