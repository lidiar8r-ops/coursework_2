from src.api import HeadHunterAPI, AreaAPI

from src.config import URL_HH
from src.vacancies import Vacancy


# Создание экземпляра класса для работы с API сайтов с вакансиями
def user_interaction():
    """ Функция для взаимодействия с пользователем"""

    # search_query = input("Введите поисковый запрос: ")
    # area = (input("Введите город: ")
    # top_n = int(input("Введите количество вакансий для вывода в топ N (не больше 20): "))
    # filter_words = input("Введите ключевые слова для фильтрации вакансий: ").split()
    # salary_range = input("Введите диапазон зарплат: ") # Пример: 100000 - 150000

    platforms = ["HeadHunter"]
    search_query = 'Python'
    top_n = int(15)
    filter_words = ("программист разработчик php").split()
    salary_range = "100000 - 150000"
    area = "Челябинск"


    # Получение id города для поиска вакансий с hh.ru
    id_area = AreaAPI(area).get_id_area()

    # Получение вакансий с hh.ru в формате JSON
    hh_api = HeadHunterAPI(URL_HH+"vacancies")
    hh_vacancies = hh_api.get_vacancies(search_query, id_area)

    # Преобразование набора данных из JSON в список объектов
    vacancies_list = Vacancy.cast_to_object_list(hh_vacancies)

    # # Пример работы контструктора класса с одной вакансией
    # vacancy = Vacancy("Python Developer", "<https://hh.ru/vacancy/123456>", "100 000-150 000 руб.",
    #                   "Требования: опыт работы от 3 лет...", "", "")

    filtered_vacancies = vacancies_list.filter_vacancies(vacancies_list, filter_words)

    ranged_vacancies = vacancies_list.get_vacancies_by_salary(filtered_vacancies, salary_range)

    sorted_vacancies = vacancies_list.sort_vacancies(ranged_vacancies)
    top_vacancies = vacancies_list.get_top_vacancies(sorted_vacancies, top_n)
    print_vacancies(top_vacancies)

    # Сохранение информации о вакансиях в файл
    json_saver = JSONSaver()
    json_saver.add_vacancy(vacancy)
    json_saver.delete_vacancy(vacancy)


if __name__ == "__main__":
    user_interaction()