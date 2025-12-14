import json
from pathlib import Path
from unittest.mock import patch

import pytest
import requests

from src.api import AreaAPI


def create_temp_file(filename: Path, content: dict):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)


def remove_temp_file(filename: str):
    filepath = Path(filename)
    if filepath.exists():
        filepath.unlink()


def test_get_id_area_from_api_success(area_api, temp_filename, valid_areas_data):
    remove_temp_file(temp_filename)
    with patch.object(area_api, "_request", return_value=valid_areas_data):
        assert area_api.get_id_area() == "1"


def test_get_id_area_from_file_success(area_api, temp_filename, valid_areas_data):
    create_temp_file(Path(temp_filename), valid_areas_data)
    assert area_api.get_id_area() == "1"


def test_get_id_area_file_invalid_json(area_api, temp_filename):
    with open(temp_filename, "w", encoding="utf-8") as f:
        f.write("Это не JSON!")
    with patch.object(area_api, "get_requests", return_value=None):
        assert area_api.get_id_area() == "0"


def test_get_id_area_network_error(area_api, temp_filename):
    remove_temp_file(temp_filename)
    with patch.object(area_api, "_request", side_effect=requests.exceptions.RequestException("Network error")):
        with patch("src.api.logger.error") as mock_log:
            area_id = area_api.get_id_area()

    assert area_id == "0"
    assert mock_log.called
    assert "Network error" in str(mock_log.call_args[0][0])


def test_find_area_id_nested_success(area_api, valid_areas_data):
    area_id = area_api.find_area_id(valid_areas_data, "Ленинградская область")
    assert area_id == "78"


def test_find_area_id_not_found(area_api, valid_areas_data):
    area_id = area_api.find_area_id(valid_areas_data, "Новосибирск")
    assert area_id == "0"


def test_save_data_success(area_api, temp_filename, valid_areas_data):
    temp_path = Path(temp_filename)
    remove_temp_file(temp_filename)

    area_api._save_data(valid_areas_data)
    assert temp_path.exists()

    with temp_path.open("r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert saved_data == valid_areas_data


def test_save_data_io_error(area_api, temp_filename):
    with patch("builtins.open", side_effect=IOError("Permission denied")):
        with patch("src.api.logger.error") as mock_log:
            area_api._save_data({"data": "test"})
    assert mock_log.call_count >= 1


@pytest.mark.parametrize(
    "area_name,expected_id",
    [
        ("Москва", "1"),
        ("Санкт‑Петербург", "2"),
        ("Ленинградская область", "78"),
        ("Новосибирск", "0"),
    ],
)
def test_find_area_id_parametrized(area_api, area_name, expected_id, valid_areas_data):
    area_id = area_api.find_area_id(valid_areas_data, area_name)
    assert area_id == expected_id


def test_find_area_id_invalid_input():

    api = AreaAPI(area="Москва")  # создаём экземпляр

    # Перебираем разные некорректные варианты данных
    for data in [
        None,  # None
        "",  # пустая строка
        0,  # ноль (число)
        1,  # любое число
        True,  # булево
        3.14,  # дробное число
        b"bytes",  # байты
        set(),  # множество
        tuple(),  # кортеж
        "текст",  # строка
    ]:
        result = api.find_area_id(data, "Москва")
        assert result == "0", f"Для {data} ожидался '0', но получено {result}"


def test_find_area_id_dict_input():
    from src.api import AreaAPI

    api = AreaAPI(area="Москва")

    # Входной словарь (один регион)
    data = {"id": "1", "name": "Москва", "areas": []}

    # Вызываем метод с dict-входом
    result = api.find_area_id(data, "Москва")

    # Проверяем, что нашёл ID "1"
    assert result == "1", f"Ожидался '1', но получено {result}"


def test_find_area_id_nested_found():
    from src.api import AreaAPI

    api = AreaAPI(area="Ленинградская область")

    data = [
        {"id": "2", "name": "Санкт‑Петербург", "areas": [{"id": "78", "name": "Ленинградская область", "areas": []}]}
    ]

    result = api.find_area_id(data, "Ленинградская область")
    assert result == "78", f"Ожидался '78', но получено {result}"


def test_get_id_area_handles_none_from_api():
    from src.api import AreaAPI

    api = AreaAPI(area="Москва", filename="dummy.json")

    with patch.object(api, "get_requests", return_value=None):
        result = api.get_id_area()

    assert result == "0", f"Ожидался '0', но получено {result}"


def test_get_id_area_handles_unexpected_exception():
    api = AreaAPI(area="Москва", filename="temp_nonexistent.json")

    with patch("src.api.logger.error") as mock_logger:  # Заглушаем и контролируем
        with patch.object(api, "get_requests", side_effect=ValueError("Искусственная ошибка")):
            result = api.get_id_area()

    # Проверяем, что logger.error был вызван ровно 1 раз
    assert mock_logger.call_count == 1
    # Проверяем, что в сообщении есть текст ошибки
    assert "Искусственная ошибка" in mock_logger.call_args[0][0]
    # Проверяем возврат значения
    assert result == "0"
