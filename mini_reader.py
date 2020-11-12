from abc import ABC
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from os import path, makedirs
from html.parser import HTMLParser


class ExtractorText(HTMLParser, ABC):
    def __init__(self):
        self.text = ''
        self.list_tegs = list()
        self.is_news = False
        self.is_text = False
        super(ExtractorText, self).__init__()

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and not self.is_news:
            for attr in attrs:
                if attr[0] == 'itemtype' and attr[1] == 'http://schema.org/NewsArticle':
                    self.list_tegs.append(tag)
                    self.is_news = True
                    print(tag, attrs)
        if self.is_news:
            if tag == 'h1' or tag == 'p' or tag == 'div':
                self.is_text = True
                self.list_tegs.append(tag)
                print(tag)
            if tag == 'a':
                self.is_text = True
                self.list_tegs.append(tag)
                for attr in attrs:
                    if attr[0] == 'href':
                        self.cur_link = attr[1]
                print(tag)

    def handle_endtag(self, tag):
        if self.is_news:
            if tag == 'h1' or tag == 'p' or tag == 'div' or tag == 'a':
                self.list_tegs.pop()
                print(tag)
        if self.is_news == True and len(self.list_tegs) == 0:
            self.is_news = False
            self.is_text = False

    def handle_data(self, data):
        if self.is_text:
            if self.list_tegs[-1] == 'h1' or self.list_tegs[-1] == 'p':
                self.text += data + '\n' * 2
                self.is_text = False
                print("Encountered some data  :", data)
            if self.list_tegs[-1] == 'a':
                self.text += data + f' [{self.cur_link}] '

    def feed(self, data):
        super(ExtractorText, self).feed(data)
        print(self.text)
        return self.text


class MiniReader:
    def __init__(self, url):
        self.request = Request(url)
        self.parser = ExtractorText()
        self._get_page()
        self._extract_text()
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
        self.page = self.parser.feed(self.page)
        print()
