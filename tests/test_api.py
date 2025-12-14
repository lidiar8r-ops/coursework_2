import json
import os
from unittest.mock import patch, MagicMock
import pytest
import requests

from src.api import AreaAPI



# Вспомогательные функции
def create_temp_file(filename: str, content: dict):
    """Создаёт временный JSON‑файл."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)


def remove_temp_file(filename: str):
    """Удаляет временный файл, если он существует."""
    if os.path.exists(filename):
        os.remove(filename)



# Тестовые данные
VALID_AREAS_DATA = {
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

INVALID_JSON = "Это не JSON!"



# Фикстуры
@pytest.fixture
def temp_filename():
    return "test_areas.json"

@pytest.fixture
def area_api(temp_filename):
    return AreaAPI(area="Москва", filename=temp_filename)



# Тесты
def test_get_id_area_from_api_success(area_api, temp_filename):
    """Тест: ID получен через API (файла нет)."""
    remove_temp_file(temp_filename)

    with patch.object(area_api, '_request', return_value=VALID_AREAS_DATA):
        with patch.object(area_api, '_save_data') as mock_save:
            area_id = area_api.get_id_area()

    assert area_id == "1"
    mock_save.assert_called_once()
    assert os.path.exists(temp_filename)


def test_get_id_area_from_file_success(area_api, temp_filename):
    """Тест: ID прочитан из файла."""
    create_temp_file(temp_filename, VALID_AREAS_DATA)
    area_id = area_api.get_id_area()
    assert area_id == "1"

def test_get_id_area_file_invalid_json(area_api, temp_filename):
    """Тест: файл с невалидным JSON."""
    with open(temp_filename, "w", encoding="utf-8") as f:
        f.write(INVALID_JSON)

    with patch.object(area_api, 'get_vacancies', return_value=None):
        area_id = area_api.get_id_area()


    assert area_id == 0

def test_get_id_area_network_error(area_api, temp_filename):
    """Тест: ошибка сети при запросе."""
    remove_temp_file(temp_filename)

    with patch.object(area_api, '_request', side_effect=requests.exceptions.RequestException("Network error")):
        with patch('src.app_logger.logger.error') as mock_log:
            area_id = area_api.get_id_area()

    assert area_id == 0
    assert mock_log.call_count >= 1

def test_find_area_id_nested_success(area_api):
    """Тест: поиск во вложенных областях."""
    area_id = area_api.find_area_id(VALID_AREAS_DATA, "Ленинградская область")
    assert area_id == "78"

def test_find_area_id_not_found(area_api):
    """Тест: область не найдена."""
    area_id = area_api.find_area_id(VALID_AREAS_DATA, "Новосибирск")
    assert area_id == 0

def test_save_data_success(area_api, temp_filename):
    """Тест: успешное сохранение данных."""
    remove_temp_file(temp_filename)
    area_api._save_data(VALID_AREAS_DATA)
    assert os.path.exists(temp_filename)


    with open(temp_filename, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert saved_data == VALID_AREAS_DATA

def test_save_data_io_error(area_api, temp_filename):
    """Тест: ошибка записи в файл."""
    with patch('builtins.open', side_effect=IOError("Permission denied")):
        with patch('src.app_logger.logger.error') as mock_log:
            area_api._save_data({"data": "test"})

    assert mock_log.call_count >= 1

@pytest.mark.parametrize("area_name,expected_id", [
    ("Москва", "1"),
    ("Санкт‑Петербург", "2"),
    ("Ленинградская область", "78"),
    ("Новосибирск", 0),
])
def test_find_area_id_parametrized(area_api, area_name, expected_id):
    """Параметризованный тест для find_area_id."""
    area_id = area_api.find_area_id(VALID_AREAS_DATA, area_name)
    assert area_id == expected_id


# Очистка после тестов
@pytest.fixture(autouse=True)
def cleanup(temp_filename):
    yield
    remove_temp_file(temp_filename)
