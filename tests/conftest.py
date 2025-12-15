import os

import pytest

from src.area import AreaAPI
from src.config import DATA_DIR
from src.vacancies import Vacancy
from src.work_files import JSONSaver


@pytest.fixture(scope="function")
def temp_filename():
    """Имя временного файла в директории data."""
    filename = os.path.join(DATA_DIR, "test_areas.json")
    # Удаляем файл перед тестом, если он существует (чистая среда)
    if os.path.exists(filename):
        os.remove(filename)
    yield filename
    # Очистка после теста
    if os.path.exists(filename):
        os.remove(filename)


@pytest.fixture(scope="function")
def area_api(temp_filename):
    """Экземпляр AreaAPI с временным файлом."""
    return AreaAPI("Москва", filename=str(temp_filename))


@pytest.fixture(scope="function")
def valid_areas_data():
    """Тестовые данные для областей."""
    return [
        {"id": "1", "name": "Москва", "lat": 55.749646, "lng": 37.62368, "areas": []},
        {"id": "2", "name": "Санкт‑Петербург", "lat": 59.9398, "lng": 30.3158, "areas": []},
        {"id": "78", "name": "Ленинградская область", "lat": 60.0, "lng": 30.5, "areas": []},
    ]


@pytest.fixture(scope="function")
def invalid_json():
    """Невалидные JSON-данные."""
    return "Это не JSON!"


@pytest.fixture(scope="function")
def vacancies_list():
    """Фикстура с тестовыми данными вакансий."""
    return [
        {
            "title": "Python Developer",
            "url": "https://hh.ru/vacancy/12345",
            "salary": "150 000 – 200 000 руб.",
            "description": "Разработка на Python",
            "employer": "ООО ТехСофт",
            "published_at": "2025-12-15T10:00:00+0300",
        },
        {
            "title": "Junior Python",
            "url": "https://hh.ru/vacancy/67890",
            "salary": "",
            "description": "Базовые задачи",
            "employer": "ООО Старт",
            "published_at": "2025-12-16T09:00:00+0300",
        },
    ]


@pytest.fixture(scope="function")
def invalid_paths():
    """Список некорректных путей к файлам."""
    return ["", " ", "/invalid/path/with/null\x00.json", "../bad:name|.json"]


# Тестовые данные
@pytest.fixture
def sample_vacancy():
    return Vacancy(
        title="Python Developer",
        url="https://hh.ru/123",
        salary="150000",
        description="Разработка на Python",
        employer="ООО ТехСофт",
        published_at="2025-12-15T10:00:00",  # или другая дата
    )


@pytest.fixture
def json_saver_temp_file():
    """Временный файл для тестов JSONSaver."""
    return "test_vacancies_temp.json"


@pytest.fixture
def json_saver(tmp_path):
    """Экземпляр JSONSaver с временным файлом (автоматически удаляется)."""
    temp_file = tmp_path / "test_vacancies.json"
    saver = JSONSaver(filename=str(temp_file))
    return saver

