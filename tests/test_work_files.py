import pytest
import json
import os
import re  # ← Добавлено для parse_salary (если используется)
from unittest.mock import patch, mock_open
from datetime import datetime

# Импорты тестируемых компонентов
from src.vacancies import Vacancy
from src.work_files import JSONSaver


def getdefault_filename() -> str:
    """Возвращает имя файла по умолчанию в формате: vacancies_YYYYMMDD_HHMMSS.json."""
    now = datetime.now()
    return f"vacancies_{now.strftime('%Y%m%d_%H%M%S')}.json"

def test_json_saver_init_creates_empty_list(json_saver):
    """Проверка инициализации: пустой список вакансий."""
    assert json_saver.vacancies == []

def test_add_vacancy_success(json_saver, sample_vacancy):
    """Проверка успешного добавления вакансии."""
    result = json_saver._add_vacancy(sample_vacancy)
    assert result is True
    assert len(json_saver.vacancies) == 1
    assert json_saver.vacancies[0].url == sample_vacancy.url  # ← без скобок

def test_add_vacancy_duplicate(json_saver, sample_vacancy):
    """Проверка защиты от дубликатов по URL."""
    json_saver._add_vacancy(sample_vacancy)
    result = json_saver._add_vacancy(sample_vacancy)  # Повторное добавление
    assert result is False
    assert len(json_saver.vacancies) == 1  # Количество не изменилось

def test_save_data_writes_json(json_saver, sample_vacancy, json_saver_temp_file):
    """Проверка сохранения данных в JSON-файл."""
    json_saver._add_vacancy(sample_vacancy)
    json_saver._save_data()

    # Проверяем, что файл создан
    assert os.path.exists(json_saver_temp_file)

    # Читаем файл и проверяем содержимое
    with open(json_saver_temp_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 1
    assert data[0]["title"] == "Python Developer"
    assert data[0]["url"] == "https://hh.ru/123"
    assert data[0]["salary"] == "150000"
    assert data[0]["employer"] == "ООО ТехСофт"
    assert data[0]["published_at"] == "2025-12-15T10:00:00"

def test_load_data_reads_json(json_saver_temp_file, sample_vacancy):
    """Проверка загрузки данных из JSON-файла."""
    json_saver = JSONSaver(json_saver_temp_file)

    with open(json_saver_temp_file, "w", encoding="utf-8") as f:
        json.dump([sample_vacancy.to_dict()], f, ensure_ascii=False, indent=4)

    json_saver._load_data()
    assert len(json_saver.vacancies) == 1

    loaded = json_saver.vacancies[0]
    assert loaded.title == sample_vacancy.title
    assert loaded.url == sample_vacancy.url
    assert loaded.salary == sample_vacancy.salary
    assert loaded.employer == sample_vacancy.employer
    assert loaded.published_at == sample_vacancy.published_at


def test_delete_vacancy_success(json_saver, sample_vacancy):
    """Проверка удаления вакансии по URL."""
    json_saver._add_vacancy(sample_vacancy)
    result = json_saver.delete_vacancy(sample_vacancy)
    assert result is True
    assert len(json_saver.vacancies) == 0

def test_delete_vacancy_not_found(json_saver, sample_vacancy):
    """Проверка удаления несуществующей вакансии."""
    result = json_saver.delete_vacancy(sample_vacancy)
    assert result is False


def test_filter_by_keyword(json_saver, sample_vacancy):
    """Проверка фильтрации по ключевому слову."""
    json_saver._add_vacancy(sample_vacancy)
    filtered = json_saver.filter_by_keyword("Python")

    assert len(filtered) == 1
    # Если title — свойство:
    assert filtered[0].title == "Python Developer"
    # Если title — метод:
    # assert filtered[0].title() == "Python Developer"


def test_get_top_by_salary(json_saver):
    """Проверка выборки топ-N по зарплате."""
    v1 = Vacancy(
        title="A",
        url="https://example.com/1",
        salary="100000",
        description="",
        employer="Работодатель 1",
        published_at="2025-12-15T10:00:00"
    )
    v2 = Vacancy(
        title="B",
        url="https://example.com/2",
        salary="200000",
        description="",
        employer="Работодатель 2",
        published_at="2025-12-15T11:00:00"
    )
    v3 = Vacancy(
        title="C",
        url="https://example.com/3",
        salary="150000",
        description="",
        employer="Работодатель 3",
        published_at="2025-12-15T12:00:00"
    )

    for v in [v1, v2, v3]:
        json_saver._add_vacancy(v)

    top_2 = json_saver.get_top_by_salary(2)
    assert len(top_2) == 2
    assert top_2[0].salary == "200000"  # Самая высокая зарплата
    assert top_2[1].salary == "150000"



def test_clear_method(json_saver, sample_vacancy):
    """Проверка очистки хранилища."""
    json_saver._add_vacancy(sample_vacancy)
    json_saver.clear()
    assert len(json_saver.vacancies) == 0

    # Файл должен существовать, но быть пустым
    with open(json_saver.filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == []

@patch("builtins.open", new_callable=mock_open)
def test_save_data_logs_error_on_exception(mock_file):
    """Проверка логирования ошибки при сохранении."""
    saver = JSONSaver("invalid_path.json")
    saver.vacancies = [
        Vacancy(
            title="Test",
            url="https://example.com",
            salary="100",
            description="",
            employer="",
            published_at="2025-12-15T10:00:00"
        )
    ]

    # Имитируем ошибку записи
    mock_file.side_effect = OSError("Disk full")

    with pytest.raises(OSError):
        saver._save_data()

@patch("builtins.open", side_effect=FileNotFoundError("File not found"))
def test_load_data_handles_missing_file(mock_file):
    """Проверка обработки отсутствующего файла при загрузке."""
    saver = JSONSaver("missing.json")
    saver._load_data()  # Не должно вызывать исключение
    assert saver.vacancies == []  # Список остаётся пустым

@patch("builtins.open", side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
def test_load_data_handles_invalid_json(mock_file):
    """Проверка обработки некорректного JSON."""
    saver = JSONSaver("bad.json")
    saver._load_data()
    assert saver.vacancies == []  # Список остаётся пустым
