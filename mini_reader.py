from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class MiniReader:
    def __init__(self, url):
        self.request = Request(url)
        self._get_page()
        self._save_to_file()

    def _get_page(self):
        try:
            with urlopen(self.request) as response:
                self.code = response.code
                self.context_type = response.headers.get('Content-Type')
                if 'charset=' in self.context_type:
                    self.charset = self.context_type.split()[-1]
                    self.charset = self.charset.split('=')[-1]
                self.page = response.read().decode(self.charset)
        except HTTPError as err:
            self.code = err.code
            self.page = err.reason

    def _save_to_file(self):
        with open('1.txt', 'w', encoding=self.charset) as file:
            file.write(self.page)

