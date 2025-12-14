"""
Тесты для модуля AreaAPI.
Проверяют работу с API hh.ru, файлами и логированием.
"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock

from src.api import AreaAPI


class TestAreaAPI(unittest.TestCase):

    def setUp(self):
        """Подготовка перед каждым тестом."""
        self.test_filename = "test_areas.json"
        self.area_api = AreaAPI(area="Москва", filename=self.test_filename)

    def tearDown(self):
        """Удаление тестового файла после каждого теста."""
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    @patch('src.api_hh.logger')
    def test_get_id_area_file_not_exists_and_request_ok(self, mock_logger):
        """Тест: файла нет → запрос к API, поиск ID."""
        with patch.object(self.area_api, '_request', return_value={
            "areas": [
                {"id": "1", "name": "Москва", "areas": []}
            ]
        }):
            area_id = self.area_api.get_id_area()

        self.assertEqual(area_id, "1")
        mock_logger.error.assert_not_called()

    @patch('src.api_hh.logger')
    def test_get_id_area_file_exists_and_found(self, mock_logger):
        """Тест: файл есть → читаем, находим ID."""
        test_data = {"areas": [{"id": "78", "name": "Санкт-Петербург", "areas": []}]}
        with open(self.test_filename, "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)

        area_id = self.area_api.get_id_area()
        self.assertEqual(area_id, "0")
        mock_logger.error.assert_not_called()


    def test_get_id_area_file_invalid_json(self):
        """Тест: файл с невалидным JSON → ошибка."""
        with open(self.test_filename, "w", encoding="utf-8") as f:
            f.write("не JSON")

        area_id = self.area_api.get_id_area()
        self.assertEqual(area_id, "0")


    def test_get_id_area_request_fails(self):
        """Тест: ошибка запроса к API → возврат '0'."""
        with patch.object(self.area_api, '_request', side_effect=Exception("Network error")):
            area_id = self.area_api.get_id_area()

        self.assertEqual(area_id, "0")


    def test_find_area_id_found_in_nested(self):
        """Тест: поиск ID во вложенных областях."""
        data = {
            "areas": [
                {
                    "id": "1",
                    "name": "Центральный ФО",
                    "areas": [
                        {"id": "77", "name": "Москва", "areas": []},
                        {"id": "50", "name": "Московская область", "areas": []}
                    ]
                }
            ]
        }
        area_id = self.area_api.find_area_id(data, "Москва")
        self.assertEqual(area_id, 77)

    def test_find_area_id_not_found(self):
        """Тест: область не найдена → возвращает 0."""
        data = {"areas": [{"id": "1", "name": "Не Москва", "areas": []}]}
        area_id = self.area_api.find_area_id(data, "Москва")
        self.assertEqual(area_id, 0)

    @patch('src.api_hh.logger')
    def test_save_data_success(self, mock_logger):
        """Тест: сохранение данных в файл → успех."""
        test_data = {"test": "data"}
        self.area_api._save_data(test_data)

        self.assertTrue(os.path.exists(self.test_filename))
        with open(self.test_filename, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, test_data)


    @patch('src.api_hh.logger')
    def test_save_data_io_error(self, mock_logger):
        """Тест: ошибка записи файла → лог ошибки."""
        # Мокируем open для имитации IOError
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            self.area_api._save_data({"data": "test"})

        mock_logger.info.assert_not_called()

    @patch('src.api_hh.logger')
    def test_save_data_type_error(self, mock_logger):
        # Подготавливаем НЕсериализуемые данные (вызовут TypeError)
        class NonSerializable:
            def __repr__(self):
                return "<NonSerializable object>"

        test_data = {
            "valid_key": "value",
            "invalid_obj": NonSerializable()  # Этот объект нельзя сериализовать в JSON
        }

        # Вызываем метод — ожидаем, что он перехватит TypeError
        self.area_api._save_data(test_data)
