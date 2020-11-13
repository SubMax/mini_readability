from html.parser import HTMLParser
from abc import ABC
from settings import ATTR_SCHEME_DICT, TEXT_TAG_DICT


class Door:
    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = attrs
        self.data = ''
        self.is_open = True
        self.is_opened = False

    def add_data(self, data):
        self.data += data
        self.is_opened = True

    def __repr__(self):
        return f'[{self.tag}, {self.attrs}, {self.data}]'


class ExtractorText(HTMLParser, ABC):
    def __init__(self):
        self.text = ''
        self.list_tegs = list()
        self.doors = []
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

        if self.is_news:
            if TEXT_TAG_DICT.get(tag, False):
                self.is_text = True
                self.list_tegs.append(tag)
                self.doors.append(Door(tag, attrs))
                for attr in attrs:
                    if attr[0] == 'href':
                        self.cur_link = attr[1]

    def handle_endtag(self, tag):
        if self.is_news:
            if TEXT_TAG_DICT.get(tag, False):
                self.list_tegs.pop()
                for door in self.doors[::-1]:
                    if door.tag == tag and door.is_open:
                        door.is_open = False
                        break
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
                for door in self.doors[::-1]:
                    if door.is_open and door.tag == self.list_tegs[-1]:
                        door.add_data(data)
                        break

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
