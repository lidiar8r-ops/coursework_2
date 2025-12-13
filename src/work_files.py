import json
import os

from abc import ABC, abstractmethod
from typing import List

from src import app_logger
from src.config import filename_vacan
from src.vacancies import Vacancy


# Настройка логирования
logger = app_logger.get_logger("work_files.log")


class VacancyStorage(ABC):
    """АБСТРАКТНЫЙ КЛАСС ДЛЯ ХРАНЕНИЯ ВАКАНСИЙ"""
    @abstractmethod
    def _add_vacancy(self, vacancy: Vacancy) -> None:
        pass

    @abstractmethod
    def get_vacancies(self) -> List[Vacancy]:
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy: Vacancy) -> bool:
        pass

    @abstractmethod
    def filter_by_keyword(self, keyword: str) -> List[Vacancy]:
        pass

    @abstractmethod
    def get_top_by_salary(self, n: int) -> List[Vacancy]:
        pass


class JSONSaver(VacancyStorage):
    """ РЕАЛИЗАЦИЯ ХРАНЕНИЯ В JSON"""
    def __init__(self, filename: str = filename_vacan):
        self.filename = filename
        self.vacancies: List[Vacancy] = []
        self._load_data()


    def _add_vacancy(self, vacancy: Vacancy) -> bool:
        if self._is_duplicate(vacancy.url()):
            # print(f"Дубликат: вакансия с URL {vacancy.url()} уже существует.")
            logger.info(f"Дубликат: вакансия с URL {vacancy.url()} уже существует.")
            return False

        self.vacancies.append(vacancy)
        self._save_data()
        # print(f"Вакансия {vacancy.title()} добавлена.")
        return True


    def get_all(self) -> List[Vacancy]:
        return self.vacancies


    def clear(self) -> None:
        self.vacancies = []
        self._save_data()
        print("Файл очищен.")
        logger.info("Файл очищен.")


    def _save_data(self) -> None:
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(
                    [v.to_dict() for v in self.vacancies],
                    f,
                    ensure_ascii=False,
                    indent=4
                )
        except Exception as e:
            print(f"Ошибка при записи в файл {self.filename}: {e}")
            logger.error(f"Ошибка при записи в файл {self.filename}: {e}")
            raise


    def _load_data(self) -> None:
        if not os.path.exists(self.filename):
            self.vacancies = []
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.vacancies = [
                    Vacancy(
                        title=item["title"],
                        url=item["url"],
                        salary=item["salary"],
                        description=item["description"],
                        employer=item["employer"],
                        published_at=item["published_at"]
                    )
                    for item in data
                ]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Ошибка при чтении файла {self.filename}: {e}")
            logger.error(f"Ошибка при чтении файла {self.filename}: {e}")
            self.vacancies = []


    def _is_duplicate(self, url: str) -> bool:
        return any(v.url() == url for v in self.vacancies)


    def get_vacancies(self) -> List[Vacancy]:
        return self.vacancies


    def delete_vacancy(self, vacancy: Vacancy) -> bool:
        for i, v in enumerate(self.vacancies):
            if v.url() == vacancy.url():
                del self.vacancies[i]
                self._save_data()
                return True
        return False


    def filter_by_keyword(self, keyword: str) -> List[Vacancy]:
        keyword_lower = keyword.lower()
        return [
            v for v in self.vacancies
            if (keyword_lower in v.title().lower() or
                keyword_lower in v.description().lower())
        ]


    def get_top_by_salary(self, n: int) -> List[Vacancy]:
        sorted_vacancies = sorted(self.vacancies, reverse=True)
        return sorted_vacancies[:n]


        # Заглушки для будущей интеграции с БД

    def update_vacancy(self, vacancy: Vacancy) -> bool:
        return False


    def filter_by_salary_range(self, min_salary: float, max_salary: float) -> List[Vacancy]:
        return [
            v for v in self.vacancies
            if min_salary <= v.get_salary_value() <= max_salary
        ]


    def filter_by_employer(self, employer: str) -> List[Vacancy]:
        employer_lower = employer.lower()
        return [v for v in self.vacancies if employer_lower in v.employer().lower()]
