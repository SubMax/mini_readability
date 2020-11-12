from abc import ABC
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from os import path, makedirs
from html.parser import HTMLParser

ATTR_NAME_DICT = {
    'itemprop': {
        'articleBody': 'articleBody',
        'headline': 'headline',
        'description': 'description',
        'alternativeHeadline': 'alternativeHeadline',
    },
}
ATTR_SCHEME_DICT = {
    'itemtype': {
        'http://schema.org/NewsArticle': 'http://schema.org/NewsArticle',
        'http://schema.org/Article': 'http://schema.org/Article',
    }
}

TEXT_TAG_DICT = {
    'h1': 'h1',
    'p': 'p',
    'a': 'a',
    # 'div': 'div',
    # 'span': 'span',
}

TAG_DICT = {
    'div': 'div',
    'article': 'article',
}


class ExtractorText(HTMLParser, ABC):
    def __init__(self):
        self.text = ''
        self.list_tegs = list()
        self.target_tag = ''
        self.is_news = False
        self.is_text = False
        self.cur_link = ''
        super(ExtractorText, self).__init__()

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if ATTR_SCHEME_DICT.get(attr[0], False):
                scheme = ATTR_SCHEME_DICT.get(attr[0])
                if scheme.get(attr[1], False):
                    self.is_news = True
                    self.list_tegs.append(tag)
                    print(self.getpos())

        if self.is_news:
            if TEXT_TAG_DICT.get(tag, False):
                self.is_text = True
                self.list_tegs.append(tag)
                print(tag, attrs)
                for attr in attrs:
                    if attr[0] == 'href':
                        self.cur_link = attr[1]

    def handle_endtag(self, tag):
        if self.is_news:
            if TEXT_TAG_DICT.get(tag, False):
                self.list_tegs.pop()
                print(tag)
        if self.is_news == True and len(self.list_tegs) == 0:
            self.is_news = False
            self.is_text = False

    def handle_data(self, data):
        if self.is_text:
            if TEXT_TAG_DICT.get(self.list_tegs[-1], False):
                if self.list_tegs[-1] == 'a':
                    self.text += data + f' [{self.cur_link}] '
                else:
                    self.text += data + f' <{self.list_tegs[-1]}> '
                    self.is_text = False
                print(data)

    def feed(self, data):
        super(ExtractorText, self).feed(data)
        self.format_text()
        return self.text

    def format_text(self):
        line = ''
        output_text = ''
        for word in self.text.split():
            if TEXT_TAG_DICT.get(word[1:-1], False) and TEXT_TAG_DICT.get(word[1:-1], False) != 'a':
                line += '\n\n'
                output_text += line
                line = ''
            else:
                if len(line + word) > 80:
                    line += '\n'
                    output_text += line
                    line = ''
                else:
                    line += word + ' '
        self.text = output_text


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
