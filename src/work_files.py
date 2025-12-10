from abc import ABC


class JSONWorks(ABC):
    def __init(self, name_file: str):
        self.name_file = os.path.abspath(os.path.join(os.path.abspath(__file__), "..\\data\\"+name_file))

   def existense_file(self):
       # Проверка существования файла
       if not os.path.isfile(self.name_file):
           logger.error(f"Не найден файл {path_filename}")
           return result_df






class JSONSaver():
    """абстрактный класс, который обязывает реализовать методы для добавления вакансий в файл, получения данных из
    файла по указанным критериям и удаления информации о вакансиях. Создать класс для сохранения информации о вакансиях
    в JSON-файл. Дополнительно, по желанию, можно реализовать классы для работы с другими форматами, например
    с CSV- или Excel-файлом, с TXT-файлом.
    Данный класс выступит в роли основы для коннектора, заменяя который (класс-коннектор), можно использовать в
    качестве хранилища одну из баз данных или удаленное хранилище со своей специфической системой обращений.
    В случае если какие-то из методов выглядят не используемыми для работы с файлами, то не стоит их удалять.
    Они пригодятся для интеграции к БД. Сделайте заглушку в коде.
    """
    pass

    def __init__(self, vacancy):
        self.vacancy = vacancy

    def add_vacancy(self, vacancy):
        pass

    def delete_vacancy(self, vacancy):
        pass
