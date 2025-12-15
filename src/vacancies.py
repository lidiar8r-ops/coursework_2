import logging
import re
from typing import Any, Dict, List
from urllib.parse import urlparse

# Настройка логирования
logger = logging.getLogger("vacancy")


class Vacancy:
    """
    Представляет собой одну вакансию с основными атрибутами и методами для работы с ними.

    Основные атрибуты:
        title (str): Название вакансии.
        url (str): Адрес страницы вакансии.
        salary (str): Зарплата (может содержать диапазон или фиксированное значение).
        description (str): Краткое описание вакансии.
        employer (str): Работодатель.
        published_at (str): Дата публикации вакансии.

    Методы:
        get_salary_value() -> float: Возвращает численное значение зарплаты для сортировки.
        to_dict() -> Dict[str, Any]: Преобразует объект в словарь для дальнейшей сериализации.
        from_hh_api(item: Dict[str, Any]) -> Vacancy: Создает объект Vacancy из ответа API hh.ru.
        print_vacancies(vacancies: List['Vacancy']): Печать информации о списке вакансий.
    """

    def __init__(self, title: str, url: str, salary: str, description: str, employer: str, published_at: str):
        """
        Конструктор класса Vacancy.

        Args:
            title (str): Название вакансии.
            url (str): URL вакансии.
            salary (str): Информация о зарплате.
            description (str): Описание вакансии.
            employer (str): Название работодателя.
            published_at (str): Дата публикации вакансии.

        Raises:
            ValueError: Если обязательные поля отсутствуют или некорректны.
        """
        # Валидация обязательных полей
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
        """
        Проверяет корректность URL.

        Args:
            url (str): URL для проверки.

        Returns:
            bool: True, если URL корректен, иначе False.
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _process_salary(self, salary: str) -> str:
        """
        Приводит зарплату к унифицированному формату отображения.

        Args:
            salary (str): Строка с информацией о зарплате.

        Returns:
            str: Унифицированная строка с зарплатой ("Зарплата не указана", если поле пустое).
        """
        if salary is None:
            return "Зарплата не указана!"
        salary_clean = salary.strip()
        return salary_clean if salary_clean else "Зарплата не указана!"

    def get_salary_value(self) -> float:
        """
        Вычисляет числовое значение зарплаты для сравнительного анализа.

        Например, извлекает цифры из строки вроде "от 50 000 руб." или "80 000—100 000 руб."

        Returns:
            float: Среднее значение зарплаты или 0, если зарплата не указана.
        """
        if "Зарплата не указана!" in self._salary:
            return 0.0

        # Ищем числа (возможно, с пробелами-разделителями тысяч)
        numbers = re.findall(
            r"\b\d{1,3}(?:\s?\d{3})*\b", self._salary.replace("\u202f", "")
        )  # "\u202f" — неразрывный пробел
        values = []

        for num_str in numbers:
            cleaned = num_str.replace(" ", "")
            try:
                values.append(float(cleaned))
            except ValueError:
                continue  # Пропускаем некорректные строки

        if len(values) >= 2:
            return sum(values) / len(values)  # Среднее арифметическое
        elif values:
            return values[0]  # Единственное значение
        else:
            return 0.0  # Значение зарплаты не извлечено

    # Геттеры для свойств объекта
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

    # Сеттер для изменения зарплаты (с предварительной обработкой)
    def set_salary(self, value: str) -> None:
        self._salary = self._process_salary(value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует объект в словарь для последующей сериализации в JSON.

        Returns:
            Dict[str, Any]: Словарь с данными вакансии.
        """
        data = {
            "title": self._title,
            "url": self._url,
            "salary": self._salary,
            "description": self._description,
            "employer": self._employer,
            "published_at": self._published_at,
        }

        # Проверка, что каждое значение не является методом (для надежности сериализации)
        for key, value in data.items():
            if callable(value):
                logger.error(f"Поле '{key}' содержит метод, а не значение: {value}")
                raise TypeError(f"Поле '{key}' содержит метод, а не значение: {value}")

        return data

    @classmethod
    def from_hh_api(cls, item: Dict[str, Any]) -> "Vacancy":
        """
        Создает объект Vacancy из ответа API hh.ru.

        Args:
            item (Dict[str, Any]): Данные вакансии из API hh.ru.

        Returns:
            Vacancy: Новый объект Vacancy.
        """
        salary_info = item.get("salary")
        salary_str = ""

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

        return cls(
            title=item["name"],
            url=item["alternate_url"],
            salary=salary_str,
            description=item.get("snippet", {}).get("requirement", "") or "",
            employer=item.get("employer", {}).get("name", ""),
            published_at=item.get("published_at", ""),
        )

    # Операции сравнения (по зарплате)
    def __lt__(self, other: "Vacancy") -> bool:
        return self.get_salary_value() < other.get_salary_value()

    def __le__(self, other: "Vacancy") -> bool:
        return self.get_salary_value() <= other.get_salary_value()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.get_salary_value() == other.get_salary_value()

    # Строковое представление
    def __str__(self) -> str:
        return f"{self._title} ({self._salary}) — {self._url}"

    def __repr__(self) -> str:
        return (
            f"Vacancy(title='{self._title}', url='{self._url}', "
            f"salary='{self._salary}', employer='{self._employer}', published_at='{self._published_at}')"
        )

    @staticmethod
    def print_vacancies(vacancies: List["Vacancy"]) -> None:
        """
        Выводит информацию о вакансиях в удобной форме.

        Args:
            vacancies (List[Vacancy]): Список вакансий для вывода.
        """
        logger.info("Вывод в консоль информации о вакансиях")
        for i, vacancy in enumerate(vacancies, start=1):
            print(f"{i}. {vacancy.title()}")
            print(f"Зарплата: {vacancy.salary()}")
            print(f"Описание: {vacancy.description()[:100]}...")  # Ограничили вывод первых 100 символов
            print(f"Работодатель: {vacancy.employer()}")
            print(f"Ссылка: {vacancy.url()}")
            print("-" * 50)
