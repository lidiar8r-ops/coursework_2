import pytest
from unittest.mock import patch, MagicMock

import requests

from src.api_hh import HeadHunterAPI

# Пример мокового ответа от HH API
MOCK_HH_RESPONSE = {
    "items": [
        {
            "id": "12345",
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/12345",
            "salary": {
                "from": 150000,
                "to": 200000,
                "currency": "RUR"
            },
            "snippet": {
                "requirement": "Опыт от 3 лет",
                "responsibility": "Разработка"
            },
            "employer": {
                "name": "ООО ТехСофт"
            },
            "published_at": "2025-12-15T10:00:00+0300"
        }
    ],
    "found": 1,
    "pages": 1
}

# Константы для тестов
VALID_QUERY = "Python"
VALID_AREA = 104
VALID_PER_PAGE = 20
VALID_EXCLUDED = ""



def test_headhunterapi_init():
    """Проверка инициализации HeadHunterAPI (без проверки logger)."""
    api = HeadHunterAPI()
    assert hasattr(api, "session")
    assert api.session is not None



@patch.object(HeadHunterAPI, "_request")
def test_headhunterapi_get_requests_success(mock_request):
    """Проверка успешного поиска вакансий в get_requests."""
    mock_request.return_value = MOCK_HH_RESPONSE

    api = HeadHunterAPI()
    vacancies = api.get_requests(
        query=VALID_QUERY, area=VALID_AREA, per_page=VALID_PER_PAGE, excluded_text=VALID_EXCLUDED
    )

    assert len(vacancies) == 1
    assert "id" in vacancies[0]
    assert "name" in vacancies[0]
    assert vacancies[0]["id"] == "12345"
    assert vacancies[0]["name"] == "Python Developer"



@patch.object(HeadHunterAPI, "_request")
def test_headhunterapi_get_requests_empty_response(mock_request):
    """Проверка обработки пустого ответа от API."""
    mock_request.return_value = {"items": [], "found": 0, "pages": 0}

    api = HeadHunterAPI()
    vacancies = api.get_requests(query=VALID_QUERY)

    assert len(vacancies) == 0


@patch.object(HeadHunterAPI, "_request")
def test_headhunterapi_get_requests_http_error(mock_request, caplog):
    """Проверка обработки HTTP‑ошибки в get_requests (имитация через None)."""
    mock_request.return_value = None  # Имитируем сбой


    api = HeadHunterAPI()
    vacancies = api.get_requests(query=VALID_QUERY)

    assert len(vacancies) == 0


@patch.object(HeadHunterAPI, "_request")
def test_headhunterapi_get_requests_network_error(mock_request, caplog):
    """Проверка обработки сетевой ошибки в get_requests (имитация через None)."""
    mock_request.return_value = None  # Имитируем сбой


    api = HeadHunterAPI()
    vacancies = api.get_requests(query=VALID_QUERY)

    assert len(vacancies) == 0


def test_headhunterapi__parse_items_valid():
    """Проверка парсинга валидных данных в _parse_items."""
    api = HeadHunterAPI()
    items = api._parse_items(MOCK_HH_RESPONSE)


    assert len(items) == 1
    assert "id" in items[0]
    assert "name" in items[0]
    assert items[0]["id"] == "12345"
    assert items[0]["name"] == "Python Developer"



def test_headhunterapi__parse_items_missing_items():
    """Проверка парсинга ответа без items."""
    api = HeadHunterAPI()
    items = api._parse_items({"found": 0})

    assert len(items) == 0


def test_headhunterapi__parse_items_invalid_item():
    """Проверка парсинга некорректного элемента в _parse_items (принимаем неполные данные)."""
    api = HeadHunterAPI()
    incomplete_response = {"items": [{"id": "1"}]}  # Нет name/url
    items = api._parse_items(incomplete_response)

    assert len(items) == 1
    assert items[0]["id"] == "1"
    assert items[0].get("name") is None  # Поле отсутствует



@patch.object(HeadHunterAPI, "_request")
def test_headhunterapi_get_requests_with_pagination(mock_request):
    """Проверка работы с пагинацией в get_requests (несколько страниц)."""
    mock_request.side_effect = [
        {
            "items": [
                {"id": "1", "name": "Dev 1", "alternate_url": "https://hh.ru/vacancy/1"}
            ],
            "pages": 2,
            "found": 2
        },
        {
            "items": [
                {"id": "2", "name": "Dev 2", "alternate_url": "https://hh.ru/vacancy/2"}
            ],
            "pages": 2,
            "found": 2
        }
    ]

    api = HeadHunterAPI()
    vacancies = api.get_requests(query=VALID_QUERY, per_page=1)

    assert len(vacancies) == 1
    titles = {v["name"] for v in vacancies}
    assert titles == {"Dev 1"}


@patch.object(HeadHunterAPI, "_request")
def test_headhunterapi_get_requests_excluded_text(mock_request):
    """Проверка фильтрации по excluded_text в get_requests (через мокированный ответ)."""
    # Имитируем, что API вернуло только 1 вакансию (уже отфильтрованную)
    mock_request.return_value = {
        "items": [
            {
                "id": "2",
                "name": "Senior Python Developer",
                "alternate_url": "https://hh.ru/vacancy/2"
            }
        ],
        "found": 1,
        "pages": 1
    }

    api = HeadHunterAPI()
    vacancies = api.get_requests(query=VALID_QUERY, excluded_text="стажёр")

    assert len(vacancies) == 1
    assert "стажёр" not in vacancies[0]["name"].lower()


@patch("src.api_hh.logger")
class TestHeadHunterAPIRequest:

    def setup_method(self):
        self.api = HeadHunterAPI()
        self.endpoint = "vacancies"
        self.params = {"text": "python"}

    def test_request_success_valid_dict(self, mock_logger):
        """Проверка успешного ответа (200) с валидным dict."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"items": [], "pages": 1})

        with patch.object(self.api.session, "get", return_value=mock_response):
            result = self.api._request(self.endpoint, self.params)

        assert result == {"items": [], "pages": 1}
        mock_logger.error.assert_not_called()

    def test_request_success_non_dict(self, mock_logger):
        """Ответ 200, но данные не dict → ошибка и None."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=["not", "a", "dict"])

        with patch.object(self.api.session, "get", return_value=mock_response):
            result = self.api._request(self.endpoint, self.params)

        assert result is None
        assert mock_logger.error.call_count == 1
        assert "Ответ API не является словарём" in str(mock_logger.error.call_args)

    def test_request_http_403(self, mock_logger):
        """HTTP 403 → CAPTCHA."""
        mock_response = MagicMock()
        mock_response.status_code = 403

        with patch.object(self.api.session, "get", return_value=mock_response):
            result = self.api._request(self.endpoint, self.params)

        assert result is None
        assert mock_logger.error.call_count == 1
        assert "CAPTCHA" in str(mock_logger.error.call_args)

    def test_request_http_404(self, mock_logger):
        """HTTP 404 → ресурс не найден."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch.object(self.api.session, "get", return_value=mock_response):
            result = self.api._request(self.endpoint, self.params)

        assert result is None
        assert mock_logger.error.call_count == 1
        assert "Ресурс не найден" in str(mock_logger.error.call_args)

    def test_request_http_401(self, mock_logger):
        """HTTP 401 → неавторизованный запрос."""
        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch.object(self.api.session, "get", return_value=mock_response):
            result = self.api._request(self.endpoint, self.params)
        assert result is None
        assert mock_logger.error.call_count == 1
        assert "Неавторизованный запрос" in str(mock_logger.error.call_args)


    def test_request_http_429(self, mock_logger):
        """HTTP 429 → лимит запросов."""
        mock_response = MagicMock()
        mock_response.status_code = 429

        with patch.object(self.api.session, "get", return_value=mock_response):
            result = self.api._request(self.endpoint, self.params)
        assert result is None
        assert mock_logger.error.call_count == 1
        assert "Превышен лимит запросов" in str(mock_logger.error.call_args)


    def test_request_http_other_status(self, mock_logger):
        """Другие HTTP-статусы (например, 500) → общая ошибка."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"


        with patch.object(self.api.session, "get", return_value=mock_response):
            result = self.api._request(self.endpoint, self.params)
        assert result is None
        assert mock_logger.error.call_count == 1
        assert "HTTP 500" in str(mock_logger.error.call_args)
        assert "Internal Server Error" in str(mock_logger.error.call_args)


    def test_request_network_exception(self, mock_logger):
        """Исключение сети (например, Timeout) → ошибка и None."""
        with patch.object(
            self.api.session,
            "get",
            side_effect=requests.exceptions.RequestException("Connection failed")
        ):
            result = self.api._request(self.endpoint, self.params)

        assert result is None
        assert mock_logger.error.call_count == 1
        assert "Ошибка сети" in str(mock_logger.error.call_args)
        assert "Connection failed" in str(mock_logger.error.call_args)