class Vacancy():
    """класс для работы с вакансиями. В этом классе атрибуты: название вакансии,
    ссылка на вакансию, зарплата, требования, краткое описание, адрес, график работы.
    Класс должен поддерживать методы сравнения вакансий между собой по зарплате и валидировать данные,
    которыми инициализируются его атрибуты."""
    pass
    # Способами валидации данных - проверка указана или нет зарплата.
    # В этом случае выставлять значение зарплаты 0 или «Зарплата не указана» в зависимости от структуры класса.
    # Vacancy("Python Developer", "<https://hh.ru/vacancy/123456>", "100 000-150 000 руб.", "Требования: опыт работы от 3 лет...")
    def __init__(self, name: str, link: str, pay: str, requirements: str, description: str, addres: str = "",
                 shedule: str = ""):
        self.name = name
        self.link = link
        if not pay:
            print("Зарплата не указана")
            self.pay = 0
        else:
            self.pay = pay
        self.requirements = requirements
        self.description = description
        self.adress = addres
        self.shedule = shedule



    # @property
    def cast_to_object_list(hh_vacancies):
        """Преобразование набора данных из JSON в список объектов"""
        pass

    def filter_vacancies(self, vacancies_list: list, filter_words: list) -> list:
        """Фильтрация вакансий по словам"""
        pass


    def get_vacancies_by_salary(self, filtered_vacancies, salary_range):
        """Фильтрация вакансий по диапазону зарплат"""
        pass


    def sort_vacancies(ranged_vacancies):
        """сортировка вакансий"""
        pass


    def get_top_vacancies(sorted_vacancies, top_n):
        """Вывод вакансий, входящих в топ top_n, выводит первые n вакансий"""
        pass

    def print_vacancies(self, top_vacancies):
        pass



