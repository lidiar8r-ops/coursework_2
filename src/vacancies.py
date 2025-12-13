import re
from urllib.parse import urlparse
from typing import Dict, Any, List
import logging


# Настройка логирования (если ещё не настроена)
logger = logging.getLogger("vacancy")

class Vacancy:
    """Класс, представляющий вакансию."""


    def __init__(self, title: str, url: str, salary: str, description: str, employer: str, published_at: str):
        # Валидация обязательных полей
        # if not title or not title.strip():
        #     logger.error("Название вакансии обязательно")
        #     raise ValueError("Название вакансии обязательно")
        if not url or not url.strip():
            logger.error("URL вакансии обязателен")
            raise ValueError("URL вакансии обязателен")

        if not self._is_valid_url(url.strip()):
            logger.error(f"Некорректный URL: {url}")
            raise ValueError(f"Некорректный URL: {url}")


        self._title = title.strip()
        self._url = url.strip()
        self._salary = self._process_salary(salary)
        self._description = description.strip() if description and description.strip() else "Описание не указано"
        self._employer = employer.strip() if employer and employer.strip() else "Работодатель не указан"
        self._published_at = (published_at or "").strip()


    def _is_valid_url(self, url: str) -> bool:
        """Проверяет корректность URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _process_salary(self, salary: str) -> str:
        """Обрабатывает строку с зарплатой, возвращая корректное представление."""
        if salary is None:
            return "Зарплата не указана"
        salary_clean = salary.strip()
        return salary_clean if salary_clean else "Зарплата не указана"


    def get_salary_value(self) -> float:
        """
        Возвращает числовое значение зарплаты для сравнения.
        Извлекает числа, игнорируя разделители тысяч.
        """
        if "Зарплата не указана!" in self._salary:
            return 0.0

        # Ищем числа (с пробелами-разделителями тысяч или без)
        numbers = re.findall(r"\b\d{1,3}(?:\s?\d{3})*\b", self._salary.replace(" ", ""))
        values = []

        for num_str in numbers:
            cleaned = num_str.replace(" ", "")  # убираем пробелы-разделители
            try:
                values.append(int(cleaned))
            except ValueError:
                continue  # пропускаем нечисловые строки


        if len(values) >= 2:
            return sum(values) / len(values)  # среднее значение
        elif values:
            return float(values[0])  # единственное значение
        else:
            return 0.0  # если чисел не найдено

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

    def published_at(self) -> str:
        return self._published_at

    # Сеттер для зарплаты (с валидацией)
    def set_salary(self, value: str):
        self._salary = self._process_salary(value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует объект в словарь для JSON-сериализации.
        Проверяет, что все значения — не методы/функции.
        """
        data = {
            "title": self._title,
            "url": self._url,
            "salary": self._salary,
            "description": self._description,
            "employer": self._employer,
            "published_at": self._published_at
        }

        # Отладочная проверка: нет ли методов в значениях
        for key, value in data.items():
            if callable(value):
                logger.error(f"Поле '{key}' содержит метод, а не значение: {value}")
                raise TypeError(f"Поле '{key}' содержит метод, а не значение: {value}")


        return data

    @classmethod
    def from_hh_api(cls, item: Dict[str, Any]) -> 'Vacancy':
        """Создаёт объект Vacancy из данных API hh.ru."""
        salary_info = item.get("salary")
        salary_str = None


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

        # Если salary_info нет или поля пустые — оставляем None


        return cls(
            title=item["name"],
            url=item["alternate_url"],
            salary=salary_str,
            description=item.get("snippet", {}).get("requirement", "") or "",
            employer=item.get("employer", {}).get("name", ""),
            published_at=item.get("published_at", "")
        )

    # Методы сравнения (по зарплате)
    def __lt__(self, other: 'Vacancy') -> bool:
        return self.get_salary_value() < other.get_salary_value()


    def __le__(self, other: 'Vacancy') -> bool:
        return self.get_salary_value() <= other.get_salary_value()


    def __eq__(self, other: 'Vacancy') -> bool:
        return self.get_salary_value() == other.get_salary_value()


    # Строковое представление
    def __str__(self) -> str:
        return f"{self._title} ({self._salary}) — {self._url}"

    def __repr__(self) -> str:
        return (f"Vacancy(title='{self._title}', url='{self._url}', "
                f"salary='{self._salary}', employer='{self._employer}', published_at='{self._published_at}')")

    @staticmethod
    def print_vacancies(vacancies: List["Vacancy"]):
        """Вывод в консоль информацию о вакансии"""
        logger.info("Вывод в консоль информацию о вакансиях")
        for i, vacancy in enumerate(vacancies, 1):
            print(f"{i}. {vacancy.title()}")
            print(f"Зарплата: {vacancy.salary()}")
            print(f"Описание: {vacancy.description()[:100]}...")
            print(f"Работодатель: {vacancy.employer()}")
            print(f"Ссылка: {vacancy.url()}")
            print("=" * 50)