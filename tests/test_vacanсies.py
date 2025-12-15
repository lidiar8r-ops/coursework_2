import pytest
from datetime import datetime
from src.vacancies import Vacancy




# Тестовые данные
VALID_DATA = {
    "title": "Python Developer",
    "url": "https://hh.ru/vacancy/12345",
    "salary": "150 000 – 200 000 руб.",
    "description": "Разработка на Python",
    "employer": "ООО ТехСофт",
    "published_at": "2025-12-15T10:00:00+0300"
}

INVALID_DATA = [
    ({}, "Обязательное поле 'title' отсутствует"),
    ({"title": ""}, "Поле 'title' не может быть пустым"),
    ({"title": "Dev", "url": ""}, "Поле 'url' не может быть пустым"),
    ({"title": "Dev", "url": "not-a-url"}, "Некорректный URL"),
    ({"published_at": "invalid-date"}, "Некорректный формат даты"),
]

HH_ITEM_VALID = {
    "id": "12345",
    "name": "Python Developer",
    "alternate_url": "https://hh.ru/vacancy/12345",
    "salary": {"from": 150000, "to": 200000, "currency": "RUR"},
    "snippet": {"requirement": "Опыт 3+ года", "responsibility": "Писать код"},
    "employer": {"name": "ООО ТехСофт"},
    "published_at": "2025-12-15T10:00:00+0300"
}


HH_ITEM_NO_SALARY = {
    "name": "Junior Dev",
    "alternate_url": "https://hh.ru/vacancy/67890",
    "salary": None,
    "snippet": {},
    "employer": {"name": "ООО Старт"},
    "published_at": "2025-12-16T09:00:00+0300"
}




def test_vacancy_init_valid():
    """Проверка создания объекта с корректными данными."""
    vacancy = Vacancy(**VALID_DATA)
    assert vacancy.title == VALID_DATA["title"]
    assert vacancy.url == VALID_DATA["url"]
    assert vacancy.salary == VALID_DATA["salary"]
    assert isinstance(vacancy.published_at, datetime)




@pytest.mark.parametrize("data,error_msg", INVALID_DATA)
def test_vacancy_init_invalid(data, error_msg):
    """Проверка валидации при создании объекта."""
    with pytest.raises(ValueError, match=error_msg):
        Vacancy(**data)




def test_vacancy_to_dict():
    """Проверка метода to_dict()."""
    vacancy = Vacancy(**VALID_DATA)
    result = vacancy.to_dict()


    assert isinstance(result, dict)
    assert result["title"] == VALID_DATA["title"]
    assert result["url"] == VALID_DATA["url"]
    assert result["salary"] == VALID_DATA["salary"]
    assert isinstance(result["published_at"], str)
    assert result["published_at"].startswith("2025-12-15")




def test_vacancy_str():
    """Проверка строкового представления."""
    vacancy = Vacancy(**VALID_DATA)
    expected = f"Vacancy(title='{VALID_DATA['title']}', url='{VALID_DATA['url']}')"
    assert str(vacancy) == expected




def test_vacancy_repr():
    """Проверка repr()."""
    vacancy = Vacancy(**VALID_DATA)
    repr_str = repr(vacancy)
    assert "Vacancy(" in repr_str
    assert f"title='{VALID_DATA['title']}'" in repr_str
    assert f"url='{VALID_DATA['url']}'" in repr_str




def test_vacancy_eq():
    """Проверка сравнения объектов (==) по URL."""
    v1 = Vacancy(**VALID_DATA)
    v2 = Vacancy(**VALID_DATA)
    assert v1 == v2

    data2 = VALID_DATA.copy()
    data2["url"] = "https://hh.ru/vacancy/999"
    v3 = Vacancy(**data2)
    assert v1 != v3




def test_vacancy_hash():
    """Проверка хешируемости (для set/dict)."""
    v1 = Vacancy(**VALID_DATA)
    v2 = Vacancy(**VALID_DATA)
    assert hash(v1) == hash(v2)


    data3 = VALID_DATA.copy()
    data3["url"] = "https://hh.ru/vacancy/888"
    v3 = Vacancy(**data3)
    assert hash(v1) != hash(v3)



def test_from_hh_api_valid():
    """Проверка создания Vacancy из ответа HH.ru."""
    vacancy = Vacancy.from_hh_api(HH_ITEM_VALID)


    assert vacancy.title == "Python Developer"
    assert vacancy.url == "https://hh.ru/vacancy/12345"
    assert vacancy.salary == "150 000 – 200 000 руб."
    assert "Опыт 3+ года" in vacancy.description
    assert "Писать код" in vacancy.description
    assert vacancy.employer == "ООО ТехСофт"
    assert isinstance(vacancy.published_at, datetime)




def test_from_hh_api_no_salary():
    """Проверка обработки отсутствия зарплаты в ответе HH.ru."""
    vacancy = Vacancy.from_hh_api(HH_ITEM_NO_SALARY)

    assert vacancy.salary == ""
    assert vacancy.title == "Junior Dev"
    assert vacancy.employer == "ООО Старт"




def test_from_hh_api_missing_fields():
    """Проверка обработки отсутствующих обязательных полей."""
    # Нет name и alternate_url
    item = {"id": "1"}

    with pytest.raises(KeyError, match="Обязательное поле 'name' отсутствует"):
        Vacancy.from_hh_api(item)

    # Есть name, но нет alternate_url
    item["name"] = "Dev"
    with pytest.raises(KeyError, match="Обязательное поле 'alternate_url' отсутствует"):
        Vacancy.from_hh_api(item)




def test_from_hh_api_invalid_date():
    """Проверка обработки некорректной даты."""
    item = HH_ITEM_VALID.copy()
    item["published_at"] = "не-дата"


    with pytest.raises(ValueError, match="Некорректный формат даты"):
        Vacancy.from_hh_api(item)



def test_salary_formatting():
    """Проверка форматирования зарплаты в from_hh_api."""
    # Полный диапазон
    item = HH_ITEM_VALID
    vacancy = Vacancy.from_hh_api(item)
    assert vacancy.salary == "150 000 – 2 Newton 000 руб."  # Ожидаем корректный формат

    # Только 'to'
    item["salary"]["from"] = None
    vacancy = Vacancy.from_hh_api(item)
    assert vacancy.salary == "до 200 000 руб."


    # Только 'from'
    item["salary"]["to"] = None
    item["salary"]["from"] = 100000
    vacancy = Vacancy.from_hh_api(item)
    assert vacancy.salary == "от 100 000 руб."


    # Нет зарплаты
    item["salary"] = None
    vacancy = Vacancy.from_hh_api(item)
    assert vacancy.salary == ""



def test_description_concat():
    """Проверка сборки описания из фрагментов snippet."""
    item = {
        "snippet": {
            "requirement": "Знание Python и Django",
            "responsibility": "Разработка веб‑приложений"
        }
    }
    vacancy = Vacancy.from_hh_api(item)

    assert "Знание Python и Django" in vacancy.description
    assert "Разработка веб‑приложений" in vacancy.description
    # Проверка, что фрагменты соединены разумно (через точку/новую строку)
    assert vacancy.description.count(".") >= 1 or "\n" in vacancy.description



def test_description_missing_requirement():
    """Проверка обработки отсутствующего поля 'requirement' в snippet."""
    item = {
        "snippet": {
            "responsibility": "Поддержка существующих сервисов"
        }
    }
    vacancy = Vacancy.from_hh_api(item)

    assert "Поддержка существующих сервисов" in vacancy.description
    assert "requirement" not in vacancy.description.lower()



def test_description_missing_responsibility():
    """Проверка обработки отсутствующего поля 'responsibility' в snippet."""
    item = {
        "snippet": {
            "requirement": "Опыт работы с SQL"
        }
    }
    vacancy = Vacancy.from_hh_api(item)

    assert "Опыт работы с SQL" in vacancy.description
    assert "responsibility" not in vacancy.description.lower()



def test_description_empty_snippet():
    """Проверка пустого snippet."""
    item = {"snippet": {}}
    vacancy = Vacancy.from_hh_api(item)

    assert vacancy.description == ""

    # Или допустимо: хотя бы пустая строка, но не None
    assert isinstance(vacancy.description, str)



def test_description_none_snippet():
    """Проверка отсутствующего snippet."""
    item = {}  # snippet вообще нет
    vacancy = Vacancy.from_hh_api(item)

    assert vacancy.description == ""
    assert isinstance(vacancy.description, str)



def test_published_at_parsing():
    """Проверка парсинга даты published_at."""
    item = {
        "published_at": "2025-12-15T10:30:00+0300",
        "name": "Test Job",
        "alternate_url": "https://test.ru"
    }
    vacancy = Vacancy.from_hh_api(item)

    assert isinstance(vacancy.published_at, datetime)
    assert vacancy.published_at.year == 2025
    assert vacancy.published_at.month == 12
    assert vacancy.published_at.day == 15
    assert vacancy.published_at.hour == 10
    assert vacancy.published_at.minute == 30




def test_published_at_invalid_format():
    """Проверка обработки некорректного формата даты."""
    item = {
        "published_at": "не-дата",
        "name": "Invalid Date Job",
        "alternate_url": "https://invalid.ru"
    }

    with pytest.raises(ValueError, match="Некорректный формат даты"):
        Vacancy.from_hh_api(item)



def test_employer_parsing():
    """Проверка извлечения названия работодателя."""
    item = {
        "employer": {"name": "ООО Новый Проект"},
        "name": "Dev",
        "alternate_url": "https://url.ru"
    }
    vacancy = Vacancy.from_hh_api(item)
    assert vacancy.employer == "ООО Новый Проект"



def test_employer_missing():
    """Проверка отсутствия поля employer."""
    item = {
        "name": "Freelance Job",
        "alternate_url": "https://freelance.ru"
    }
    vacancy = Vacancy.from_hh_api(item)
    assert vacancy.employer == ""  # или None — зависит от реализации



def test_id_in_from_hh_api():
    """Проверка, что id из HH используется как часть данных (если нужно)."""
    item = {
        "id": "98765",
        "name": "Job with ID",
        "alternate_url": "https://id.ru"
    }
    vacancy = Vacancy.from_hh_api(item)
    # Если в классе есть поле id — проверяем его
    if hasattr(vacancy, "id"):
        assert vacancy.id == "98765"
    # Иначе проверяем, что оно не сломало создание
    assert isinstance(vacancy, Vacancy)
