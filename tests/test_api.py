import json

from pathlib import Path
from unittest.mock import patch
import pytest
import requests


# Вспомогательные функции
def create_temp_file(filename: Path, content: dict):
    """Создаёт временный JSON‑файл в указанной директории."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

def remove_temp_file(filename: str):
    """Удаляет временный файл, если он существует."""
    filepath = Path(filename)  # Преобразуем str → Path
    if filepath.exists():
        filepath.unlink()  # Удаляем файл

# Тесты
def test_get_id_area_from_api_success(area_api, temp_filename, valid_areas_data):
    """Тест: ID получен через API (файла нет)."""
    remove_temp_file(temp_filename)

    with patch.object(area_api, '_request', return_value=valid_areas_data):
        result = area_api.get_id_area()
        assert result == "1" # get_id_area возвращает строку!

def test_get_id_area_from_file_success(area_api, temp_filename, valid_areas_data):
    """Тест: ID прочитан из файла."""
    create_temp_file(temp_filename, valid_areas_data)
    area_id = area_api.get_id_area()
    assert area_id == "1"


def test_get_id_area_file_invalid_json(area_api, temp_filename):
    """Тест: файл с невалидным JSON."""
    # Записываем невалидный JSON
    with open(temp_filename, "w", encoding="utf-8") as f:
        f.write("Это не JSON!")  # Невалидный JSON

    # Мокируем get_vacancies, чтобы избежать реального запроса к API
    with patch.object(area_api, 'get_vacancies', return_value=None):
        area_id = area_api.get_id_area()

    # Ожидаем, что метод вернёт "0" при ошибке
    assert area_id == "0"


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
    area_id = area_api.find_area_id(valid_areas_data, "Ленинградская область")
    assert area_id == 78


def test_find_area_id_not_found(area_api):
    """Тест: область не найдена."""
    area_id = area_api.find_area_id(valid_areas_data, "Новосибирск")
    assert area_id == 0

def test_save_data_success(area_api, temp_filename):
    """Тест: успешное сохранение данных."""
    remove_temp_file(temp_filename)
    area_api._save_data(valid_areas_data)
    assert temp_filename.exists()

    with open(temp_filename, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert saved_data == valid_areas_data

def test_save_data_io_error(area_api, temp_filename):
    """Тест: ошибка записи в файл."""
    with patch('builtins.open', side_effect=IOError("Permission denied")):
        with patch('src.app_logger.logger.error') as mock_log:
            area_api._save_data({"data": "test"})

    assert mock_log.call_count >= 1

@pytest.mark.parametrize("area_name,expected_id", [
    ("Москва", 1),
    ("Санкт‑Петербург", 2),
    ("Ленинградская область", 78),
    ("Новосибирск", 0),
])
def test_find_area_id_parametrized(area_api, area_name, expected_id):
    """Параметризованный тест для find_area_id."""
    area_id = area_api.find_area_id(valid_areas_data, area_name)
    assert area_id == expected_id

