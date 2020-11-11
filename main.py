from mini_reader import MiniReader


if __name__ == '__main__':
    print("Для выхода введите: q")
    while True:
        url = input("Введите url-адрес:")
        if url == 'q':
            print("Выход.")
            break
        else:
            mr = MiniReader(url=url)
            print(mr.page)
