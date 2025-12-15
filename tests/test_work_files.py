import pytest
import json
import os
from unittest.mock import patch, mock_open

from src.work_files import (
    save_vacancies_to_json,
    load_vacancies_from_json,
    validate_file_path,
    get_default_filename
)



# Тестовые данные
VACANCIES_LIST = [
    {
        "title": "Python Developer",
        "url": "https://hh.ru/vacancy/12345",
        "salary": "150 000 – 200 000 руб.",
        "description": "Разработка на Python",
        "employer": "ООО ТехСофт",
        "published_at": "2025-12-15T10:00:00+0300"
    },
    {
        "title": "Junior Python",
        "url": "https://hh.ru/vacancy/67890",
        "salary": "",
        "description": "Базовые задачи",
        "employer": "ООО Старт",
        "published_at": "2025-12-16T09:00:00+0300"
    }
]

INVALID_PATHS = [
    "",
    " ",
    "/invalid/path/with/null\x00.json",
    "../bad:name|.json"
]



def test_getdefault_filename():
    """Проверка генерации имени файла по умолчанию."""
    filename = getdefault_filename()
    assert filename.startswith("vacancies_")
    assert filename.endswith(".json")
    # Проверка формата даты в имени
    assert len(filename) > 15  # Минимум: "vacancies_YYYYMMDD_HHMMSS.json"




@pytest.mark.parametrize("path", INVALID_PATHS)
def test_validate_file_path_invalid(path):
    """Проверка валидации некорректных путей."""
    with pytest.raises(ValueError, match="Недопустимый путь к файлу"):
        validate_file_path(path)




def test_validate_file_path_valid_tmp():
    """Проверка валидного временного пути."""
    # Используем tmp_path из pytest для безопасного теста
    with pytest.tmp_path() as tmp:
        valid_path = tmp / "vacancies.json"
        result = validate_file_path(str(valid_path))
        assert result == str(valid_path)




@patch("builtins.open", new_callable=mock_open)
def test_save_vacancies_to_json_success(mock_file):
    """Проверка успешного сохранения вакансий в JSON."""
    save_vacancies_to_json(VACANCIES_LIST, "test.json")

    assert mock_file.called
    # Проверяем, что открыли файл на запись
    assert mock_file.call_args[0][0] == "test.json"
    assert mock_file.call_args[1]["mode"] == "w"
    # Проверяем вызов .write() с корректным JSON
    handle = mock_file()
    written = handle.write.call_args[0][0]
    data = json.loads(written)
    assert len(data) == 2
    assert data[0]["title"] == "Python Developer"

    assert data[1]["employer"] == "ООО Старт"




@patch("builtins.open", side_effect=PermissionError("No write access"))
def test_save_vacancies_to_json_permission_error(mock_file):
    """Проверка обработки ошибки прав доступа при сохранении."""
    with pytest.raises(PermissionError, match="Нет прав на запись"):
        save_vacancies_to_json(VACANCIES_LIST, "protected.json")




@patch("builtins.open", side_effect=OSError("Disk full"))
def test_save_vacancies_to_json_os_error(mock_file):
    """Проверка обработки системных ошибок при сохранении."""
    with pytest.raises(OSError, match="Ошибка файловой системы"):
        save_vacancies_to_json(VACANCIES_LIST, "full_disk.json")




@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(VACANCIES_LIST))
def test_load_vacancies_from_json_success(mock_file):
    """Проверка успешного чтения вакансий из JSON."""
    vacancies = load_vacancies_from_json("test.json")


    assert len(vacancies) == 2
    assert vacancies[0]["title"] == "Python Developer"
    assert vacancies[1]["url"] == "https://hh.ru/vacancy/67890"




@patch("builtins.open", side_effect=FileNotFoundError("File not found"))
def test_load_vacancies_from_json_not_found(mock_file):
    """Проверка обработки отсутствия файла."""
    with pytest.raises(FileNotFoundError, match="Файл не найден"):
        load_vacancies_from_json("missing.json")




@patch("builtins.open", side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
def test_load_vacancies_from_json_invalid_json(mock_file):
    """Проверка обработки невалидного JSON."""
    with pytest.raises(json.JSONDecodeError, match="Некорректный JSON"):
        load_vacancies_from_json("bad.json")




@patch("builtins.open", side_effect=PermissionError("No read access"))
def test_load_vacancies_from_json_permission_error(mock_file):
    """Проверка обработки ошибки прав доступа при чтении."""
    with pytest.raises(PermissionError, match="Нет прав на чтение"):
        load_vacancies_from_json("protected.json")




def test_load_vacancies_from_json_empty_file(tmp_path):
    """Проверка чтения пустого файла."""
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("", encoding="utf-8")


    vacancies = load_vacancies_from_json(str(empty_file))
    assert vacancies == []  # Или пустой список, если так задумано




def test_load_vacancies_from_json_nonexistent_but_valid_path():
    """Проверка пути без файла (но валидный путь)."""
    # Валидный путь, но файла нет
    path = "/tmp/nonexistent.json"  # Для Unix-систем
    if os.path.exists(path):
        os.remove(path)  # Убедимся, что файла нет


    with pytest.raises(FileNotFoundError):
        load_vacancies_from_json(path)




@patch("src.work_files.validate_file_path")
@patch("builtins.open", new_callable=mock_open)
def test_save_with_validation_call(mock_validate, mock_file):
    """Проверка, что save_vacancies_to_json вызывает валидацию пути."""
    save_vacancies_to_json(VACANCIES_LIST, "valid.json")

    assert mock_validate.called
    assert mock_validate.call_args[0][0] == "valid.json"




@patch("src.work_files.validate_file_path")
@patch("builtins.open", new_callable=mock_open)
def test_load_with_validation_call(mock_validate, mock_file):
    """Проверка, что load_vacancies_from_json вызывает валидацию пути."""
    load_vacancies_from_json("valid.json")

    assert mock_validate.called
    assert mock_validate.call_args[0][0] == "valid.json"
