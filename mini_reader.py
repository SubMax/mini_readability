from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from os import path, makedirs
from exctractor import ExtractorText


class MiniReader:
    """
    Главный класс утилиты.
    Создание запроса. Выполнение запроса. Сохранение в файл.
    """
    def __init__(self, url):
        """
        :param url: URL страницы
        """
        self.request = Request(url)
        self.parser = ExtractorText()
        self._get_page()
        self._extract_text()
        self._save_to_file()

    def _get_page(self):
        """Запрос страницы"""
        try:
            with urlopen(self.request) as response:
                self.code = response.code
                self.context_type = response.headers.get('Content-Type')    # извлекаем charset из HTTP заголовка
                if 'charset=' in self.context_type:
                    self.charset = self.context_type.split()[-1]
                    self.charset = self.charset.split('=')[-1]
                self.page = response.read().decode(self.charset)
        except HTTPError as err:
            self.code = err.code
            self.page = err.reason

    def _save_to_file(self):
        """Сохранение в файл. Путь формируется автоматически исходя из URL"""
        self.BASE_DIR, _ = path.split(path.abspath(__file__))
        self.path, self.file_name = path.split(path.normpath(self.request.selector))
        self.file_name, _ = path.splitext(self.file_name)
        self.file_name += '.txt'
        self.path = self.request.host + self.path
        self.path = path.join(self.BASE_DIR, self.path)
        if not path.exists(self.path):
            makedirs(self.path)
        with open(path.join(self.path, self.file_name), 'w', encoding=self.charset) as file:
            file.write(self.page)

    def _extract_text(self):
        """Извлечение текста статьи из html страницы"""
        self.page = self.parser.feed(self.page)
