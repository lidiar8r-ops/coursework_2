from unittest.mock import MagicMock, patch

import requests

from src.api_hh import BaseAPI, HeadHunterAPI
from src.vacancies import Vacancy

# Тестовые данные
VALID_QUERY = "Python разработчик"
VALID_AREA = 113  # Москва
VALID_PER_PAGE = 10
VALID_EXCLUDED = "стажёр, 1С"

MOCK_HH_RESPONSE = {
    "items": [
        {
            "id": "12345",
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/12345",
            "salary": {"from": 150000, "to": 200000, "currency": "RUR"},
            "snippet": {"requirement": "Опыт от 3 лет", "responsibility": "Разработка"},
            "employer": {"name": "ООО ТехСофт"},
            "published_at": "2025-12-15T10:00:00+0300",
        }
    ],
    "found": 1,
    "pages": 1,
}

EMPTY_HH_RESPONSE = {"items": [], "found": 0, "pages": 0}

NETWORK_ERROR = requests.exceptions.ConnectionError("No network")
HTTP_404_ERROR = requests.exceptions.HTTPError()
HTTP_404_ERROR.response = MagicMock(status_code=404)


def test_baseapi_init_session():
    """Проверка инициализации HTTP‑сессии в BaseAPI."""
    api = BaseAPI()
    assert hasattr(api, "session")
    assert api.session is not None
    assert isinstance(api.session, requests.Session)


@patch("requests.Session.request")
def test_baseapi__request_success(mock_request):
    """Проверка успешного HTTP‑запроса в _request."""
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = {"data": "ok"}

    api = BaseAPI()
    result = api._request("test-endpoint", {"param": "value"})

    assert result == {"data": "ok"}
    assert mock_request.called
    assert mock_request.call_args[0][0] == "GET"
    assert mock_request.call_args[1]["url"].endswith("/test-endpoint")
    assert mock_request.call_args[1]["params"] == {"param": "value"}


@patch("requests.Session.request")
def test_baseapi__request_http_error(mock_request, caplog):
    """Проверка обработки HTTP‑ошибок в _request."""
    mock_request.side_effect = HTTP_404_ERROR

    api = BaseAPI()
    result = api._request("test", {})

    assert result is None
    assert "Ошибка HTTP: 404" in caplog.text


@patch("requests.Session.request")
def test_baseapi__request_network_error(mock_request, caplog):
    """Проверка обработки сетевых ошибок в _request."""
    mock_request.side_effect = NETWORK_ERROR

    api = BaseAPI()
    result = api._request("test", {})

    assert result is None
    assert "Сетевая ошибка:" in caplog.text


@patch("requests.Session.request")
def test_baseapi__request_invalid_json(mock_request, caplog):
    """Проверка обработки невалидного JSON в _request."""
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.side_effect = ValueError("Invalid JSON")

    api = BaseAPI()
    result = api._request("test", {})

    assert result is None
    assert "Ошибка парсинга JSON:" in caplog.text


@patch.object(HeadHunterAPI, "_request")
def test_headhunterapi_get_requests_success(mock_request):
    """Проверка успешного поиска вакансий в get_requests."""
    mock_request.return_value = MOCK_HH_RESPONSE

    api = HeadHunterAPI()
    vacancies = api.get_requests(
        query=VALID_QUERY, area=VALID_AREA, per_page=VALID_PER_PAGE, excluded_text=VALID_EXCLUDED
    )

    assert len(vacancies) == 1
    assert isinstance(vacancies[0], Vacancy)
    assert vacancies[0].title == "Python Developer"
    assert vacancies[0].url == "https://hh.ru/vacancy/12345"


@patch.object(HeadHunterAPI, "_request")
def test_headhunterapi_get_requests_empty_response(mock_request):
    """Проверка пустого ответа от API в get_requests."""
    mock_request.return_value = EMPTY_HH_RESPONSE

    api = HeadHunterAPI()
    vacancies = api.get_requests(query=VALID_QUERY)

    assert len(vacancies) == 0


@patch.object(HeadHunterAPI, "_request")
def test_headhunterapi_get_requests_http_error(mock_request, caplog):
    """Проверка обработки HTTP‑ошибки в get_requests."""
    mock_request.side_effect = HTTP_404_ERROR

    api = HeadHunterAPI()
    vacancies = api.get_requests(query=VALID_QUERY)

    assert vacancies == []
    assert "Ошибка при запросе вакансий:" in caplog.text


@patch.object(HeadHunterAPI, "_request")
def test_headhunterapi_get_requests_network_error(mock_request, caplog):
    """Проверка обработки сетевой ошибки в get_requests."""
    mock_request.side_effect = NETWORK_ERROR

    api = HeadHunterAPI()
    vacancies = api.get_requests(query=VALID_QUERY)

    assert vacancies == []
    assert "Сетевая ошибка при запросе вакансий:" in caplog.text


def test_headhunterapi__parse_items_valid():
    """Проверка парсинга валидных данных в _parse_items."""
    api = HeadHunterAPI()
    items = api._parse_items(MOCK_HH_RESPONSE)

    assert len(items) == 1
    assert isinstance(items[0], Vacancy)
    assert items[0].salary == "150 000 – 200 000 руб."


def test_headhunterapi__parse_items_missing_items():
    """Проверка отсутствия поля 'items' в _parse_items."""
    api = HeadHunterAPI()
    items = api._parse_items({"wrong_key": []})

    assert items == []


def test_headhunterapi__parse_items_invalid_item():
    """Проверка парсинга некорректного элемента в _parse_items."""
    api = HeadHunterAPI()
    # Элемент без обязательных полей
    items = api._parse_items({"items": [{"id": "1"}]})

    assert items == []  # Должен пропустить невалидный элемент


@patch.object(HeadHunterAPI, "_request")
def test_headhunterapi_get_requests_with_pagination(mock_request):
    """Проверка работы с пагинацией в get_requests (несколько страниц)."""
    # Имитируем 2 страницы
    mock_request.side_effect = [
        {"items": [{"id": "1", "name": "Dev 1", "alternate_url": "url1"}], "pages": 2, "found": 2},
        {"items": [{"id": "2", "name": "Dev 2", "alternate_url": "url2"}], "pages": 2, "found": 2},
    ]

    api = HeadHunterAPI()
    vacancies = api.get_requests(query=VALID_QUERY, per_page=1)

    assert len(vacancies) == 2
    assert {v.title for v in vacancies} == {"Dev 1", "Dev 2"}
    assert all(v.url in ["url1", "url2"] for v in vacancies)


@patch.object(HeadHunterAPI, "_request")
def test_headhunterapi_get_requests_excluded_text(mock_request):
    """Проверка фильтрации по excluded_text в get_requests."""
    # Имитируем ответ с вакансиями, одна из которых содержит запрещённое слово
    mock_request.return_value = {
        "items": [
            {
                "id": "1",
                "name": "Python разработчик (стажёр)",
                "alternate_url": "url1",
                "salary": {},
                "snippet": {},
                "employer": {},
                "published_at": "2025-12-15T10:00:00+0300",
            },
            {
                "id": "2",
                "name": "Senior Python Developer",
                "alternate_url": "url2",
                "salary": {},
                "snippet": {},
                "employer": {},
                "published_at": "2025-12-15T11:00:00+0300",
            },
        ],
        "found": 2,
        "pages": 1,
    }

    api = HeadHunterAPI()
    vacancies = api.get_requests(query=VALID_QUERY, excluded_text="стажёр")

    assert len(vacancies) == 1
    assert vacancies[0].title == "Senior Python Developer"
    assert vacancies[0].url == "url2"


def test_headhunterapi_from_hh_item_salary_formatting():
    """Проверка форматирования зарплаты в _from_hh_item."""
    api = HeadHunterAPI()
    item = {"salary": {"from": 100000, "to": 150000, "currency": "RUR"}}
    vacancy = api._from_hh_item(item)
    assert vacancy.salary == "100 000 – 150 000 руб."

    # Проверка без 'from'
    item["salary"]["from"] = None
    vacancy = api._from_hh_item(item)
    assert vacancy.salary == "до 150 000 руб."

    # Проверка без 'to'
    item["salary"]["to"] = None
    item["salary"]["from"] = 100000
    vacancy = api._from_hh_item(item)
    assert vacancy.salary == "от 100 000 руб."

    # Проверка без зарплаты
    item["salary"] = None
    vacancy = api._from_hh_item(item)
    assert vacancy.salary == ""


def test_headhunterapi__from_hh_item_description_concat():
    """Проверка сборки описания из snippet в _from_hh_item."""
    api = HeadHunterAPI()
    item = {"snippet": {"requirement": "Знание Python", "responsibility": "Разработка API"}}
    vacancy = api._from_hh_item(item)
    assert "Знание Python" in vacancy.description
    assert "Разработка API" in vacancy.description

    # Проверка с отсутствующими полями
    item["snippet"]["requirement"] = None
    vacancy = api._from_hh_item(item)
    assert "Разработка API" in vacancy.description
    assert "Знание Python" not in vacancy.description


@patch("src.app_logger.get_logger")
def test_headhunterapi_logger_initialization(mock_get_logger):
    """Проверка инициализации логгера в HeadHunterAPI."""
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    api = HeadHunterAPI()

    assert api.logger is not None
    assert mock_get_logger.called
    assert mock_get_logger.call_args[0][0] == "api_hh.log"
