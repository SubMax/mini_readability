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
