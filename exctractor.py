from html.parser import HTMLParser
from settings import TEXT_TAG_DICT, LINK_TAG_DICT, FILTERS_CONTAINS, FILTERS_MATCH, FILTERS_CONTAINS_DATA, \
    ATTR_NAME_DICT, FILTERS_MATCH_DATA, LINE_WIDTH
import re


class Door:
    """Класс сущность описывающий HTML тег"""

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


class ExtractorText(HTMLParser):
    """Класс для работы с HTML"""

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
        """Метод вызывается при появлении открывающегося HTML тега"""
        self._is_the_beginning(attrs)

        if self.is_news:
            if TEXT_TAG_DICT.get(tag, False):  # Валидация имен необходимых тегов
                self.is_text = True
                self.tag_list.append(tag)
                self.doors.append(Door(tag, attrs))
            if LINK_TAG_DICT.get(tag, False):  # Если тег ссылка, сохраняем URL хранящийся в атрибуте
                for attr in attrs:
                    if attr[0] == 'href':
                        self.cur_link = attr[1]
                        self.is_link = True

    def handle_endtag(self, tag):
        """Метод вызывается при закрытии HTML тега"""
        if self.is_news:
            if TEXT_TAG_DICT.get(tag, False):
                self.tag_list.pop()
                for door in self.doors[::-1]:
                    if door.tag == tag and door.is_open:
                        door.is_open = False
                        break
        self._is_the_end()

    def handle_data(self, data):
        """Метод вызывается при появлении содержимого HTML тега"""
        if self.is_text:
            last_add_tag = self.tag_list[-1]  # последний добавленный тег / текущий, обрабатываемый тег
            if TEXT_TAG_DICT.get(last_add_tag, False):  # Если тег текстовый
                for door in self.doors[::-1]:
                    if door.is_open and door.tag == last_add_tag:
                        door.add_data(data)
                        break
                if LINK_TAG_DICT.get(last_add_tag):  # Если ссылка
                    for door in self.doors[::-1]:
                        if door.is_open and door.tag != last_add_tag:
                            door.add_data('{link}')
                            break

    def feed(self, data):
        """Метод класса HTMLParser. Дальнейшая обработка полученных данных"""
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
            if ATTR_NAME_DICT.get(attr[0], False):
                scheme = ATTR_NAME_DICT.get(attr[0])
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
        """Метод для работы с экземплярами класса Door, описывающих HTML тег"""
        self.doors = list(filter(lambda door: door.data != '', self.doors))

        def contains(door):
            """Определяет содержат ли атрибуты тега фильтры указанные в FILTERS_CONTAINS"""
            for attr in door.attrs:
                name_attr = attr[0]
                value = attr[1]
                for fltr in FILTERS_CONTAINS.get(name_attr, []):
                    if fltr in value:
                        return False
            return True

        def match(door):
            """Определяет совпадают ли атрибуты тега с фильтрами указанными в FILTERS_MATCH"""
            for attr in door.attrs:
                name_attr = attr[0]
                value = attr[1]
                for fltr in FILTERS_MATCH.get(name_attr, []):
                    if fltr == value:
                        return False
            return True

        def contains_data(door):
            """Определяет содержат ли содержимое тега фильтры указанные в FILTERS_CONTAINS_DATA"""
            for fltr in FILTERS_CONTAINS_DATA:
                if fltr in door.data:
                    return False
            return True

        def match_data(door):
            for fltr in FILTERS_MATCH_DATA:
                if fltr == door.data:
                    return False
            return True

        self.doors = list(filter(contains, self.doors))  # Применение фильтров
        self.doors = list(filter(match, self.doors))
        self.doors = list(filter(contains_data, self.doors))
        self.doors = list(filter(match_data, self.doors))

    def _format_text(self):
        """Сборка текста из экземпляров класса Door и форматирование"""
        output_text = ''
        new_text = ''

        for door in self.doors:
            if LINK_TAG_DICT.get(door.tag, False):
                for attr in door.attrs:
                    if attr[0] == 'href':
                        link = attr[1]
                output_text = re.sub(r'\{link\}', f' {door.data} [{link}] ', output_text, 1)
            else:
                output_text += door.data + '\n\n'

        fix_width = re.compile(r'[^ ].{0,%s}[\s,]' % LINE_WIDTH)  # Стрка вида '[^ ].{0,80}[\s,]'
        for line in output_text.splitlines(keepends=True):
            line = '\t' + line
            if not line == '\t\n':
                result = fix_width.findall(line)
                for new_line in result:
                    new_text += new_line + '\n'

        output_text = new_text
        self.text = output_text
