from html.parser import HTMLParser
from abc import ABC
from settings import ATTR_SCHEME_DICT, TEXT_TAG_DICT, LINK_TAG_DICT, FILTERS_CONTAINS, FILTERS_MATCH


class Door:
    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = attrs
        self.data = ''
        self.is_open = True
        self.is_opened = False

    def add_data(self, data):
        self.data += data.strip()
        self.is_opened = True

    def __repr__(self):
        return f'[{self.tag}, {self.attrs}, {self.data}]'


class ExtractorText(HTMLParser, ABC):
    def __init__(self):
        self.text = ''
        self.tag_list = list()
        self.doors = []
        self.is_news = False
        self.is_text = False
        self.is_link = False
        self.cur_link = ''
        super(ExtractorText, self).__init__()

    def handle_starttag(self, tag, attrs):
        self._is_the_beginning(attrs)

        if self.is_news:
            if TEXT_TAG_DICT.get(tag, False):
                self.is_text = True
                self.tag_list.append(tag)
                self.doors.append(Door(tag, attrs))
            if LINK_TAG_DICT.get(tag, False):
                for attr in attrs:
                    if attr[0] == 'href':
                        self.cur_link = attr[1]
                        self.is_link = True

    def handle_endtag(self, tag):
        if self.is_news:
            if TEXT_TAG_DICT.get(tag, False):
                self.tag_list.pop()
                for door in self.doors[::-1]:
                    if door.tag == tag and door.is_open:
                        door.is_open = False
                        # if not LINK_TAG_DICT.get(door.tag, False):
                        #     door.add_data(f'{tag}')
                        break
        self._is_the_end()

    def handle_data(self, data):
        if self.is_text:
            last_add_tag = self.tag_list[-1]  # последний добавленный тег
            if TEXT_TAG_DICT.get(last_add_tag, False):
                for door in self.doors[::-1]:
                    if door.is_open and door.tag == last_add_tag:
                        door.add_data(data)
                        break
                if LINK_TAG_DICT.get(last_add_tag):
                    for door in self.doors[::-1]:
                        if door.is_open and door.tag != last_add_tag:
                            door.add_data('{link}')
                            break

    def feed(self, data):
        super(ExtractorText, self).feed(data)
        self._filter_door()
        self._format_text()
        return self.text

    def _is_the_beginning(self, attrs):
        """
        Определяем начало статьи с помощью атрибутов тега.
        Доступные значения хранятся в settings.py.
        :param attrs:
        :return:
        """
        for attr in attrs:
            if ATTR_SCHEME_DICT.get(attr[0], False):
                scheme = ATTR_SCHEME_DICT.get(attr[0])
                if scheme.get(attr[1], False):
                    self.is_news = True

    def _is_the_end(self):
        """
        Определяет конец статьи.
        :return:
        """
        if self.is_news == True and len(self.tag_list) == 0:
            self.is_news = False
            self.is_text = False

    def _filter_door(self):
        self.doors = list(filter(lambda door: door.data != '', self.doors))

        def contains(door):
            for attr in door.attrs:
                name_attr = attr[0]
                value = attr[1]
                for fltr in FILTERS_CONTAINS.get(name_attr, []):
                    if fltr in value:
                        return False
            return True

        def match(door):
            for attr in door.attrs:
                name_attr = attr[0]
                value = attr[1]
                for fltr in FILTERS_MATCH.get(name_attr, []):
                    if fltr == value:
                        return False
            return True

        self.doors = list(filter(contains, self.doors))
        self.doors = list(filter(match, self.doors))

    def _format_text(self):
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
