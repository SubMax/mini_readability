from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from os import path, makedirs
from exctractor import ExtractorText


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
        self.page = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Title</title>
        </head>
        <body>
            <div class="b-topic_news hfohtqd b-topic" itemscope="" itemtype="http://schema.org/NewsArticle">
                <h1 class="lrgld b-topic__title" itemprop="headline">В Чехии предупредили об&nbsp;угрозе третьей мировой войны</h1>
                <div class="nqhr b-text js-topic__text clearfix" itemprop="articleBody">
                    <p class="noaufwg">Военная разведка Чехии предупредила об угрозе третьей мировой войны. Об этом говорится в отчете ведомства за 2019 год, который был 
                        <a href="https://www.vzcr.cz/uploads/41-Vyrocni-zprava-o-cinnosti-VZ-za-rok-2019.pdf" target="_blank" class="etxl">опубликован
                        </a> 
                    во вторник, 10 ноября.
                    </p>
                    <p class="bqwlhtt">Отмечается, что сейчас глобальный конфликт «находится на первой стадии». «Формируется мировоззрение тех, кто сможет и желает активно участвовать в нем [конфликте], и постепенно определяются технологические инструменты, с помощью которых им можно было бы управлять», — утверждают авторы доклада. По мнению аналитиков, возможной причиной конфликта является соперничество между США, Россией и Китаем.
                    </p>
                    <p class="gsxokvh">В документе также говорится о падении значимости международного права из-за отсутствия мирного диалога как способа разрешения противоречий. Авторы доклада подчеркивают, что росту напряженности способствует и манипулирование общественным сознанием.
                    </p>
                    <p class="utkrx">Ранее глава Штаба обороны Великобритании генерал 
                        <a href="https://lenta.ru/tags/persons/karter-nik/" target="_blank" class="vgygo">Ник Картер
                        </a> 
                        <a href="https://lenta.ru/news/2020/11/08/wwthree/" target="_blank" class="funsk">заявил
                        </a>
                    , что глобальная политическая нестабильность и экономический кризис из-за пандемии коронавируса могут привести к третьей мировой войне. «Мы живем в то время, когда мир представляется очень беспокойным и нестабильным, — не говоря уже о ставшей привычной глобальной конкуренции между странами. Учитывая, как много локальных конфликтов разворачивается по всей планете, риск, что из-за чьих-то просчетов произойдет эскалация, довольно реален», — заявил Картер.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        self.page = self.parser.feed(self.page)
        print()
