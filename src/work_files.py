"""
Модуль для работы с хранением и управлением вакансиями в формате JSON.
Реализует базовые операции с вакансиями, такие как сохранение, загрузка, удаление и фильтрация.
"""

# Стандартные библиотеки Python
import json  # Используется для чтения и записи данных в формате JSON
import os  # Нужен для операций с файловой системой (создание файлов, проверка существования)

# Модули сторонних разработчиков
from abc import ABC, abstractmethod  # Необходимы для реализации абстрактных классов и методов
from typing import List

# Локальные модули проекта
from src import app_logger  # Логгер для протоколирования действий программы
from src.config import filename_vacan  # Конфигурационный файл с именем файла для хранения данных
from src.vacancies import Vacancy  # Модель объекта вакансии, используемая для представления данных

# Настройка логирования
logger = app_logger.get_logger("work_files.log")


class VacancyStorage(ABC):
    """
    Абстрактный класс, задающий интерфейс для хранилища вакансий.

    Основные методы:
        add_vacancy(vacancy: Vacancy) -> None:
            Добавляет новую вакансию в хранилище.
        get_vacancies() -> List[Vacancy]:
            Возвращает список всех хранимых вакансий.
        delete_vacancy(vacancy: Vacancy) -> bool:
            Удаляет указанную вакансию из хранилища.
        filter_by_keyword(keyword: str) -> List[Vacancy]:
            Отбирает вакансии по определенному слову или фразе.
        get_top_by_salary(n: int) -> List[Vacancy]:
            Возвращает топ-N вакансий с самой высокой зарплатой.
    """

    @abstractmethod
    def _add_vacancy(self, vacancy: Vacancy) -> bool:
        """
        Добавляет вакансию в хранилище.

        Args:
            vacancy (Vacancy): Экземпляр класса Vacancy для добавления.
        """
        pass

    @abstractmethod
    def get_vacancies(self) -> List[Vacancy]:
        """
        Возвращает список всех существующих вакансий.

        Returns:
            List[Vacancy]: Список экземпляров класса Vacancy.
        """
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy: Vacancy) -> bool:
        """
        Удаляет вакансию из хранилища.

        Args:
            vacancy (Vacancy): Убираемая вакансия.

        Returns:
            bool: Результат удаления (True, если вакансия была успешно удалена).
        """
        pass

    @abstractmethod
    def filter_by_keyword(self, keyword: str) -> List[Vacancy]:
        """
        Осуществляет выборку вакансий по ключевому слову.

        Args:
            keyword (str): Ключевое слово для поиска.

        Returns:
            List[Vacancy]: Подходящие вакансии.
        """
        pass

    @abstractmethod
    def get_top_by_salary(self, n: int) -> List[Vacancy]:
        """
        Возвращает N лучших вакансий по зарплате.

        Args:
            n (int): Число лучших вакансий для выбора.

        Returns:
            List[Vacancy]: Лучшие вакансии по уровню зарплаты.
        """
        pass


class JSONSaver(VacancyStorage):
    """
    Хранит вакансии в формате JSON-файла.

    Поддерживаемые операции:
        * Добавление новых вакансий
        * Удаление вакансий
        * Фильтрация по ключевым словам
        * Выборка вакансий по уровню заработной платы
    """

    def __init__(self, filename: str = filename_vacan):
        """
        Конструктор класса JSONSaver.

        Args:
            filename (str): Имя файла для хранения данных (по умолчанию filename_vacan).
        """
        self.filename = filename
        self.vacancies: List[Vacancy] = []  # Здесь хранятся объекты вакансий
        self._load_data()  # Загружаем существующие данные из файла

    def _add_vacancy(self, vacancy: Vacancy) -> bool:
        """
        Добавляет вакансию в хранилище, если она ещё не существует.

        Args:
            vacancy (Vacancy): Вакансия для добавления.
        """
        if self._is_duplicate(vacancy.url()):
            logger.info(f"Дубликат: вакансия с URL {vacancy.url()} уже существует.")
            return False

        self.vacancies.append(vacancy)
        self._save_data()
        return True

    def get_all(self) -> List[Vacancy]:
        """
        Возвращает все вакансии из хранилища.

        Returns:
            List[Vacancy]: Список всех вакансий.
        """
        return self.vacancies

    def clear(self) -> None:
        """
        Очищает хранилище вакансий и перезаписывает файл.
        """
        self.vacancies.clear()
        self._save_data()
        logger.info("Хранилище вакансий очищено.")

    def _save_data(self) -> None:
        """
        Сохраняет вакансии в JSON-файл.
        """
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump([v.to_dict() for v in self.vacancies], file, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Ошибка при записи в файл {self.filename}: {e}")
            raise

    def _load_data(self) -> None:
        """
        Читает данные из JSON-файла и загружает их в память.
        """
        if not os.path.exists(self.filename):
            self.vacancies = []
            return

        with open(self.filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Преобразуем словари в объекты Vacancy
        self.vacancies = [
            Vacancy(
                title=item["title"],
                url=item["url"],
                salary=item["salary"],
                description=item.get("description", ""),
                employer=item["employer"],
                published_at=item["published_at"]
            )
            for item in data
        ]
        # if not os.path.exists(self.filename):
        #     self.vacancies = []
        #     return
        #
        # try:
        #     with open(self.filename, "r", encoding="utf-8") as file:
        #         data = json.load(file)
        #         self.vacancies = [Vacancy(**item) for item in data]  # Конструируем объект Vacancy из словаря
        # except (json.JSONDecodeError, KeyError, TypeError) as e:
        #     logger.error(f"Ошибка при чтении файла {self.filename}: {e}")
        #     self.vacancies = []

    def _is_duplicate(self, url: str) -> bool:
        """
        Проверяет, является ли данная вакансия дубликатом (наличие одинакового URL).

        Args:
            url (str): URL вакансии.

        Returns:
            bool: True, если такая вакансия уже существует, иначе False.
        """
        return any(v.url() == url for v in self.vacancies)

    def get_vacancies(self) -> List[Vacancy]:
        """
        Возвращает список всех вакансий.

        Returns:
            List[Vacancy]: Список вакансий.
        """
        return self.vacancies

    def delete_vacancy(self, vacancy: Vacancy, all_del: str = "нет") -> bool:
        """
        Удаляет вакансию из хранилища.

        Args:
            vacancy (Vacancy): Вакансия для удаления.
            all_del (str): Флаг полного удаления. Допустимые значения:
                "y", "да", "yes" — удалить всё;
                любое другое значение — удалить конкретную вакансию.

        Returns:
            bool: True при успешном удалении, False если вакансия не найдена.
        """
        if all_del.lower() in ("y", "да", "yes"):
            with open(self.filename, "w", encoding="utf-8"):
                self.vacancies = []
            return True

        for index, current_vacancy in enumerate(self.vacancies):
            if current_vacancy.url() == vacancy.url():
                del self.vacancies[index]
                self._save_data()
                return True
        return False

    def filter_by_keyword(self, keyword: str) -> List[Vacancy]:
        """
        Фильтрует вакансии по ключевому слову.

        Args:
            keyword (str): Ключевое слово для поиска.

        Returns:
            List[Vacancy]: Список соответствующих вакансий.
        """
        keyword_lower = keyword.lower()
        return [
            v for v in self.vacancies if keyword_lower in v.title().lower() or keyword_lower in v.description().lower()
        ]

    def get_top_by_salary(self, n: int) -> List[Vacancy]:
        """
        Возвращает топ-N вакансий по размеру зарплаты.

        Args:
            n (int): Количество лучших вакансий.

        Returns:
            List[Vacancy]: Топ-N вакансий.
        """
        sorted_vacancies = sorted(self.vacancies, key=lambda x: x.salary(), reverse=True)
        return sorted_vacancies[:n]

    # Дополнительно реализованные методы для будущих расширений функционала
    def update_vacancy(self, vacancy: Vacancy) -> bool:
        """
        Заглушка для обновления существующей вакансии.

        Args:
            vacancy (Vacancy): Новая версия вакансии.

        Returns:
            bool: Всегда возвращает False (реализация отсутствует).
        """
        return False

    def filter_by_salary_range(self, min_salary: float, max_salary: float) -> List[Vacancy]:
        """
        Фильтрует вакансии по диапазону зарплаты.

        Args:
            min_salary (float): Минимальная зарплата.
            max_salary (float): Максимальная зарплата.

        Returns:
            List[Vacancy]: Соответствующие вакансии.
        """

        def parse_salary(salary_str: str) -> float | None:
            try:
                # Удаляем пробелы и прочие разделители
                cleaned = salary_str.replace(" ", "").replace(" ", "").replace(",", "")
                return float(cleaned)
            except (ValueError, AttributeError):
                return None

        return [
            v
            for v in self.vacancies
            if (salary := parse_salary(v.salary())) is not None and min_salary <= salary <= max_salary
        ]

    def filter_by_employer(self, employer: str) -> List[Vacancy]:
        """
        Фильтрует вакансии по работодателю.

        Args:
            employer (str): Название работодателя.

        Returns:
            List[Vacancy]: Вакансии указанного работодателя.
        """
        employer_lower = employer.lower()
        return [v for v in self.vacancies if employer_lower in v.employer().lower()]
