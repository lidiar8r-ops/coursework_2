import os

import pytest

from src.api import AreaAPI
from src.config import DATA_DIR


# Фикстуры

@pytest.fixture(scope="session")
def temp_filename():
    """Имя временного файла в директории data."""
    return os.path.join(DATA_DIR, "test_areas.json")

@pytest.fixture
def area_api(temp_filename):
    return AreaAPI(area="Москва", filename=str(temp_filename))


# Тестовые данные
@pytest.fixture
def valid_areas_data():
    return {
    "areas": [
        {
            "id": "1",
            "name": "Москва",
            "areas": []
        },
        {
            "id": "2",
            "name": "Санкт‑Петербург",
            "areas": [
                {
                    "id": "78",
                    "name": "Ленинградская область",
                    "areas": []
                }
            ]
        }
    ]
}


@pytest.fixture
def invalid_json():\
    return "Это не JSON!"



# Очистка после тестов
@pytest.fixture(autouse=True)
def cleanup(temp_filename):
    yield
    remove_temp_file(temp_filename)
