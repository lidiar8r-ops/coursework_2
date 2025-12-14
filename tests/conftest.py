import os
import os
import pytest
from pathlib import Path

from src.api import AreaAPI
from src.config import DATA_DIR


# Константа с путём к данным
# DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

@pytest.fixture(scope="session")
def temp_filename():
    """Имя временного файла в директории data."""
    filename = os.path.join(DATA_DIR, "test_areas.json")
    yield filename
    # Очистка после всех тестов
    if os.path.exists(filename):
        os.remove(filename)

@pytest.fixture(autouse=True)
def cleanup(temp_filename):
    """Автоматически очищает временный файл после каждого теста."""
    yield
    # Преобразуем строку в Path для удобства
    filepath = Path(temp_filename)
    if filepath.exists():
        filepath.unlink()


@pytest.fixture
def area_api(temp_filename):
    return AreaAPI("Москва", filename=str(temp_filename))


# Тестовые данные
@pytest.fixture
def valid_areas_data():
    return [
        {
            "id": "1",
            "name": "Москва",
            "areas": [],
            "parent_id": "113",
            "utc_offset": "+03:00",
            "lat": 55.749646,
            "lng": 37.62368
        },
        {
            "id": "2",
            "name": "Санкт‑Петербург",
            "areas": [],
            "parent_id": "114",
            "utc_offset": "+03:00",
            "lat": 59.9398,
            "lng": 30.3158
        }
    ]



@pytest.fixture
def invalid_json():\
    return "Это не JSON!"
#
#
#
# # Очистка после тестов
# @pytest.fixture(autouse=True)
# def cleanup(temp_filename):
#     yield
#     remove_temp_file(temp_filename)
