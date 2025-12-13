import re
import logging
from datetime import datetime
from typing import Dict, Any

from src import app_logger

# Настройка логирования
logger = app_logger.get_logger("vacansies.log")


class Vacancy:
    """КЛАСС ВАКАНСИИ"""
    def __init__(self, title: str, url: str, salary: str, description: str, employer: str):
        # Валидация обязательных полей
        if not title or not url:
            raise ValueError("Название вакансии и URL обязательны")
        if not self._is_valid_url(url):
            raise ValueError(f"Некорректный URL: {url}")

        self._title = title.strip()
        self._url = url.strip()
        self._salary = self._process_salary(salary)
        self._description = description.strip() if description else "Описание не указано"
        self._employer = employer.strip() if employer else "Работодатель не указан"

    def _is_valid_url(self, url: str) -> bool:
        pattern = re.compile(
            r'^https?://'
            r'(?:\S+(?::\S*)?@)?'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(pattern, url) is not None

    def _process_salary(self, salary: str) -> str:
        if salary is None or salary.strip() == "":
            return "Зарплата не указана"
        return salary.strip()

    def get_salary_value(self) -> float:
        """Возвращает числовое значение зарплаты для сравнения"""
        if "Зарплата не указана!" in self._salary:
            return 0.0
        numbers = re.findall(r"\d+", self._salary)
        if numbers:
            if len(numbers) > 1:
                return (int(numbers[0]) + int(numbers[1])) / 2
            else:
                return float(numbers[0])
        return 0.0

    # Геттеры
    def title(self) -> str:
        return self._title

    def url(self) -> str:
        return self._url

    def salary(self) -> str:
        return self._salary

    def description(self) -> str:
        return self._description

    def employer(self) -> str:
        return self._employer

    # Сеттеры (опционально, с валидацией)
    def set_salary(self, value: str):
        self._salary = self._process_salary(value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self._title,
            "url": self._url,
            "salary": self._salary,
            "description": self._description,
            "employer": self._employer
        }

    @classmethod
    def from_hh_api(cls, item: Dict[str, Any]) -> 'Vacancy':
        salary_info = item.get("salary")
        if salary_info:
            salary_from = salary_info.get("from")
            salary_to = salary_info.get("to")
            currency = salary_info.get("currency", "руб.")
            if salary_from and salary_to:
                salary_str = f"{salary_from}-{salary_to} {currency}"
            elif salary_from:
                salary_str = f"от {salary_from} {currency}"
            elif salary_to:
                salary_str = f"до {salary_to} {currency}"
            else:
                salary_str = None
        else:
            salary_str = None

        return cls(
            title=item["name"],
            url=item["alternate_url"],
            salary=salary_str,
            description=item.get("snippet", {}).get("requirement", "") or "",
            employer=item.get("employer", {}).get("name", "")
        )

    # Методы сравнения
    def __lt__(self, other: 'Vacancy') -> bool:
        return self.get_salary_value() < other.get_salary_value()

    def __le__(self, other: 'Vacancy') -> bool:
        return self.get_salary_value() <= other.get_salary_value()

    def __eq__(self, other: 'Vacancy') -> bool:
        return self.get_salary_value() == other.get_salary_value()

    def __str__(self) -> str:
        return f"{self._title} ({self._salary}) — {self._url}"
