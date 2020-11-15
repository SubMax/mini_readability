# requirements.txt
Работает только со стандартной библеотекой Python
# mini_readability

    Большинство веб-страниц сейчас перегружено всевозможной рекламой…
mini_readability - утилита командной строки, которая в качестве параметра
принимает URL. Она извлекает по этому URL страницу, обрабатывает ее и
формирует текстовый файл с текстом статьи, представленной на данной странице. 
Алгоритм работает на многих сайтах и имеет настройки, расположенные в файле 
[settings.py](https://github.com/SubMax/mini_readability/blob/master/settings.py).
Имя и путь выходного файла формируется автоматически по URL. 

## Описание алгоритмов
### main.py
Главный модуль программы. Отвечает за работу с командной строкой. Ввод, вывод информации.
Создает экземпляр главного класса программы MiniReader, расположенного в mini_reader.py
```python
from mini_reader import MiniReader


if __name__ == '__main__':
    print("Утилита для сохранения текста статьи сайта в файле.\nДля выхода введите: q")
    while True:
        url = input("Введите url-адрес:")
        if url == 'q':
            print("Выход.")
            break
        else:
            mr = MiniReader(url=url)
            print(f'Файл сохранен: {mr.path}\\{mr.file_name}')
```
### mini_reader.py
Класс MiniReader, отвечает за создание http запроса и выполнение его. Из полученного http
ответа получаем html страницу, извлекаем полезную информацию и сохраняем ее в текстовый файл.
#### Метод \_\_init__
```python
def __init__(self, url):
    """
    :param url: URL страницы
    """
    self.request = Request(url)
    self.parser = ExtractorText()
    self._get_page()
    self._extract_text()
    self._save_to_file()
```
##### Создание http запроса
Создание запроса осуществляется с помощью класса 
[`Request`](https://docs.python.org/3/library/urllib.request.html#urllib.request.Request) 
модуля стандартной библиотеки 
[`urllib.request`](https://docs.python.org/3/library/urllib.request.html#module-urllib.request).
#### Метод _get_page
```python
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
```
##### Запрос
Выполнение запроса осуществляется с помощью метода 
[`urlopen`](https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen) 
модуля стандартной библиотеки 
[`urllib.request`](https://docs.python.org/3/library/urllib.request.html#module-urllib.request).
#### Метод _save_to_file
```python
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
```
##### Сохранение в файл
Сохранение в файл осуществляется с помощью встроеной функции 
[`open`](https://docs.python.org/3/library/functions.html?highlight=open#open)
Имя и путь выходного файла формируется автоматически по URL.
```commandline
Введите url-адрес:https://lenta.ru/news/2020/11/14/lazer/
Файл сохранен: [BASE_DIR]\lenta.ru\news\2020\11\14\lazer.txt
```
#### _extract_text
```python
def _extract_text(self):
    """Извлечение текста статьи из html страницы"""
    self.page = self.parser.feed(self.page)
```
##### Извлечение текста статьи из html страницы
С помощью метода `feed` экземпляра класса ExtractorText, описанного в 
[exctractor.py](https://github.com/SubMax/mini_readability/blob/master/exctractor.py), 
извлекается полезная информация из html страницы.
### exctractor.py
```python
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
```
Класс ExtractorText наследуется от 
[HTMLParser](https://docs.python.org/3/library/html.parser.html#html.parser.HTMLParser) 
и отвечает за работу с HTML. Перегруженные методы 
[`handle_starttag`](https://docs.python.org/3/library/html.parser.html#html.parser.HTMLParser.handle_starttag), 
[`handle_endtag`](https://docs.python.org/3/library/html.parser.html#html.parser.HTMLParser.handle_endtag), 
[`handle_data`](https://docs.python.org/3/library/html.parser.html#html.parser.HTMLParser.handle_data), 
[`feed`](https://docs.python.org/3/library/html.parser.html#html.parser.HTMLParser.feed) 
должны сохранять свою сигнатуру.
#### Метод feed
```python
def feed(self, data):
    """Метод класса HTMLParser. Дальнейшая обработка полученных данных"""
    super(ExtractorText, self).feed(data)
    self._filter_door()
    self._format_text()
    return self.text
```
Метод вызывает родительский метод [`feed(data)`](https://docs.python.org/3/library/html.parser.html#html.parser.HTMLParser.feed), 
который запускает обработку данных. data - HTML код, тип данных [`str`](https://docs.python.org/3/library/stdtypes.html#str). 
Затем запускаются методы фильтрации списка экземпляров класса `Door` и сборка текста из 
оставшихся экземпляров класса `Door`. Это методы `_filter_door()` и `_format_text`, 
соответственно.
#### Метод handle_starttag
```python
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
```
Метод вызывается при появлении открывающегося HTML тега. Метод `_is_the_beginning` 
вызывается для проверки атрибутов тега и устанавливает флаг `is_news`, если этот тег имеет 
нужные атрибуты.
```python
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
```
Если флаг `is_news` истина, проверяем тег по имени на соответствие текстовому. На основе 
текстового тега создаем экземпляр класса Door и добавляем его в список doors. Также 
добавляем имя тега в список `tag_list.append(tag)`, используемый для определения закрытия 
корневого тега с нужной нам текстовой информацией.
Если тег ссылочный, сохраняем URL, храняшийся в атрибуте `href`.
#### Метод handle_endtag
```python
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
```
Метод вызывается при появлении закрывающегося HTML тега. Если флаг is_news истина, 
проверяем тег по имени на соответствие текстовому. Если тег текстовый, удаляем последний 
элемент списка `tag_list.pop()`, далее начинаем обход списка `doors` экземпляров класса 
Door в обратном порядке и в последнем добавленном экземпляре с именем равным `tag` и флагом 
`is_open` равным `True` устанавливаем данный флаг `False`. То есть закрываем последний 
открытый текстовый тег.
Метод _is_the_end вызывается для проверки закрытия тега статьи и сбрасывает флаг `is_news`. 
```python
def _is_the_end(self):
    """
    Определяет конец статьи.
    :return:
    """
    if self.is_news == True and len(self.tag_list) == 0:
        self.is_news = False
        self.is_text = False
```
#### Метод handle_data
```python
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
```
Метод вызывается при появлении содержимого HTML тега. Если флаг `is_text` равен 'True', т.е. 
теги статьи уже встречались, то получаем имя последнего добавленного тега и, если тег текстовый, 
начинаем обход списка `doors` экземпляров класса Door в обратном порядке. У последнего 
добавленного экземпляра с именем равным `tag` и флагом `is_open` равным `True` вызываем метод
`add_data`. В качестве параметра метода `add_data`указываем содержимое HTML тега. Если тег 
ссылочный, вызываем метод `add_data` с параметром `{link}`.
#### Метод _filter_door
```python
    self.doors = list(filter(lambda door: door.data != '', self.doors))  # фильтрует элементы списка с пустой data
    self.doors = list(filter(contains, self.doors))  # Применение фильтров
    self.doors = list(filter(match, self.doors))
    self.doors = list(filter(contains_data, self.doors))
    self.doors = list(filter(match_data, self.doors))
```
Метод применяется для фильтрации экземпляров класса Door, описывающих HTML теги. Так как 
экземпляры хранятся в обычном списке, то применяется Built-in метод 
[filter(function, iterable)](https://docs.python.org/3/library/functions.html?highlight=open#filter),
создающий итератор из элементов `iterable`, для которых функция `function` возвращает `True`.
В качестве `function` последовательно передаем методы `contains`, `match`, `contains_data`, 
`match_data` и еще одну анонимную функцию `lambda door: door.data != ''`. Это лямбда-функция возвращает 
`False` для всех элементов, у которых `data` - пустая строка.
#### Метод contains
Определяет содержат ли атрибуты тега фильтры указанные в FILTERS_CONTAINS.
```python
    def contains(door):
        """Определяет содержат ли атрибуты тега фильтры указанные в FILTERS_CONTAINS"""
        for attr in door.attrs:
            name_attr = attr[0]
            value = attr[1]
            for fltr in FILTERS_CONTAINS.get(name_attr, []):
                if fltr in value:
                    return False
        return True
```
#### Метод match
Определяет совпадают ли атрибуты тега с фильтрами указанными в FILTERS_MATCH.
```python
    def match(door):
        """Определяет совпадают ли атрибуты тега с фильтрами указанными в FILTERS_MATCH"""
        for attr in door.attrs:
            name_attr = attr[0]
            value = attr[1]
            for fltr in FILTERS_MATCH.get(name_attr, []):
                if fltr == value:
                    return False
        return True
```
#### Метод contains_data
Определяет содержат ли содержимое тега фильтры указанные в FILTERS_CONTAINS_DATA.
```python
    def contains_data(door):
        """Определяет содержат ли содержимое тега фильтры указанные в FILTERS_CONTAINS_DATA"""
        for fltr in FILTERS_CONTAINS_DATA:
            if fltr in door.data:
                return False
        return True
```
#### Метод match_data
Определяет совпадает ли содержимое тега фильтры указанные в FILTERS_MATCH_DATA.
```python
    def match_data(door):
        """Определяет совпадает ли содержимое тега фильтры указанные в FILTERS_MATCH_DATA"""
        for fltr in FILTERS_MATCH_DATA:
            if fltr == door.data:
                return False
        return True
```
#### Метод _format_text
```python
def _format_text(self):
    """Сборка и форматирование текста из экземпляров класса Door"""
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

    fix_width = re.compile(r'[^ \w].{0,%s}[\s,\w]' % LINE_WIDTH)  # Стрка вида '[^ ].{0,80}[\s,]'
    for line in output_text.splitlines(keepends=True):
        line = '\t' + line
        if not line == '\t\n':
            result = fix_width.findall(line)
            for new_line in result:
                new_text += new_line + '\n'

    output_text = new_text
    self.text = output_text
```
Осуществляет сборку и форматирование текста из экземпляров класса Door. Пороходит по списку `doors`, 
если элемент описывает ссылочный тег заменяет в содержимом (`data`) шаблон `{link}` на строку
`f' {door.data} [{link}] '`, где `link` значение атрибута `href`. Иначе вставляет содержимое атрибута 
и добавляет пустую строку. Затем компилируем регулярное вырадение с помощью функции
[re.compile](https://docs.python.org/3/library/re.html?highlight=re#re.compile). 
В качестве параметра передаем форматируемую строку `r'[^ ].{0,%s}[\s,\w]' % LINE_WIDTH`, что 
соответствует начальной настройке `r'[^ ].{0,80}[\s,\w]'`. Данный шаблон соответствует любой строке 
не длинне 80 символов, не начинающейся с пробела и заканчивающейся на пробельный смвол или запятую, 
что дает перенос по словам или на большинство символов, которые могут быть частью слова.
Далее разбиваем, полученный на предыдущем этапе, текст по обзацам. Добавляем в начало обзаца знак 
табуляции. И если полученная строка содержит не только табуляцию и перевод на новую строку разбиваем
текст на строки шириной по 80 символов. Полученный текст сохраняем в атрибут `text` екземпляра класса
`ExtractorText`. 
### settings.py
Файл содержит настройки ширины форматирования текста `LINE_WIDTH = 80`. И филтры для поиска и фильтрации 
HTML тегов. Фильтры представляют собой наборы данных типа [dict](https://docs.python.org/3/library/stdtypes.html?highlight=dict#dict).
- ATTR_NAME_DICT - для проверки необходимых тегов статей, то есть [значения](https://schema.org/Article) атрибута `itemprop` 
- TEXT_TAG_DICT - для проверки текстовых тегов
- LINK_TAG_DICT - для проверки ссылочных тегов
- FILTERS_CONTAINS - для фильтрации тегов с именем и значением атрибутов содержащих данные строки
- FILTERS_MATCH - для фильтрации тегов с именем и значением атрибутов совпадающих с данными строками
- FILTERS_CONTAINS_DATA - для фильтрации тегов содержащих данные строки
- FILTERS_MATCH_DATA - для фильтрации тегов совпадающих с данными строками
```python
LINE_WIDTH = 80

ATTR_NAME_DICT = {
    'itemprop': {
        'articleBody': 'articleBody',
        'headline': 'headline',
        'description': 'description',
        'alternativeHeadline': 'alternativeHeadline',
    },
}

TEXT_TAG_DICT = {
    'h1': 'h1',
    'p': 'p',
    'a': 'a',
    'div': 'div',
    'span': 'span',
    'div': 'div',
    'article': 'article'
}

LINK_TAG_DICT = {
    'a': 'a',
}

FILTERS_CONTAINS = {
    'class': (
        'favorite',
        'box',
        'dark',
        'social',
        'video',
        'meta',
        'count',
        'credits',
        'photo',
        'media',
    ),
    'itemprop': (
        'date',
        'rating',
        'Rating',
        'name',
        'Name',
    ),
}

FILTERS_MATCH = {
    'class': (
        'title',
        'item',
    ),
    'itemprop': (
        'articleSection',
    ),
}

FILTERS_CONTAINS_DATA = (
    'window._',
    'window[',
    'if',
    ': "',
    'meta',
)

FILTERS_MATCH_DATA = (
    'Реклама',
)
```
## Направление дальнейшего улучшения и развития программы
