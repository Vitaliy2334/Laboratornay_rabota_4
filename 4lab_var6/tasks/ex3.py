from sqlalchemy import create_engine, func, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import json
import os.path
import hashlib
import xml.etree.ElementTree as ET

# Создаем соединение с базой данных
engine = create_engine('sqlite:///library.db', echo=False)

# Создаем базовый класс моделей
Base = declarative_base()


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    years = Column(String, nullable=False)
    books = relationship("Book", backref='author')


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    title = Column(String(100), nullable=False)
    pages = Column(Integer, nullable=False)
    publisher = Column(String(50), nullable=False)
    publication_year = Column(Integer, nullable=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)


class Library:
    def __init__(self, db_name='task3_db'):
        self.engine = create_engine(f'sqlite:///{db_name}', echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.Session = Session
        self.user = None

    def register(self, login, password):
        session = self.Session()
        user = session.query(User).filter_by(username=login, password=password).first()
        if user:
            print("такой логин уже есть в БД")
            session.close()
            return
        user = User(username=login, password=password)
        session.add(user)
        session.commit()
        session.close()

    def login(self, login, password):
        session = self.Session()
        user = session.query(User).filter_by(username=login, password=password).first()
        print(user)
        print(login)
        print(password)
        session.close()
        if user:
            self.user = user
            print(f'Пользователь {login} вошел в систему')
            return True
        else:
            print('Неправильный логин или пароль')
            return False

    def add_author(self, name, country, years, filename=None):
        session = self.Session()
        if filename:
            author = self.parse_author_file(filename)
        else:
            author = Author(name=name, country=country, years=years)
        session.add(author)
        session.commit()

        session.close()

    def add_book(self, author_id, title, pages, publisher, publication_year):
        session = self.Session()
        book = Book(author_id=author_id, title=title, pages=pages, publisher=publisher,
                    publication_year=publication_year)
        session.add(book)
        session.commit()
        session.close()

    def parse_author_file(self, filename):
        if not os.path.isfile(filename):
            print(f'Файл {filename} не существует')
            return None
        lines = None
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if lines in None:
            print(f'Файл {filename} пустой')
            return None

        author_info = {}
        for line in lines:
            key, val = line.strip().split(':', 1)
            author_info[key.lower()] = val.strip()

        name = author_info.get('name', '')
        if not name:
            print(f'Файл {filename} не содержит ключ "name" или значение пустое')
            return None

        country = author_info.get('country', '')
        years = author_info.get('years', '').split('-')

        if len(years) != 2 or not years[0].isdigit() or not years[1].isdigit():
            print(f'Файл {filename} не содержит корректного значения ключа "years". (правильный формат: 1111-2222')
            return None

        dict = {
            'name': name,
            'country': country,
            'years': [int(year) for year in years if year.isdigit()]
        }
        return dict

    def get_author_by_id(self, author_id):
        session = self.Session()
        author = session.query(Author).filter_by(id=author_id).first()
        session.close()
        return author

    def get_authors(self):
        session = self.Session()
        authors = session.query(Author).all()
        session.close()
        return authors

    def get_book_by_id(self, book_id):
        session = self.Session()
        book = session.query(Book).filter_by(id=book_id).first()
        session.close()
        return book

    def get_books(self):
        session = self.Session()
        books = session.query(Book).all()
        session.close()
        return books

    def get_author_name(self, author_id):
        session = self.Session()
        author = session.query(Author).filter_by(id=author_id).first()
        session.close()
        return author.name if author else None

    def get_book_author(self, book_id):
        session = self.Session()
        author = session.query(Author).join(Book).filter_by(id=book_id).first()
        session.close()
        return author.name if author else None

    def print_authors(self):
        authors = self.get_authors()
        for author in authors:
            print(f'{author.id} - {author.name}, {author.country}, {author.years}')

    def print_books(self):
        books = self.get_books()
        for book in books:
            author_name = self.get_book_author(book.id)
            print(
                f'{book.id} - {book.title}, {author_name}, {book.pages} pages, {book.publisher}, {book.publication_year}')

    def save_author_to_json(self, author_id):
        author = self.get_author_by_id(author_id)
        if author:
            filename = f'{author.name}.json'
            data = {
                'name': author.name,
                'country': author.country,
                'years': author.years
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            print(f'Информация об авторе {author.name} была сохранена в файле {filename}')
        else:
            print(f'Автор с id #{author_id} не найден')

    def save_author_to_xml(self, author_id):
        author = self.get_author_by_id(author_id)
        if author:
            filename = f'{author.name}.xml'
            root = ET.Element('author')
            name = ET.SubElement(root, 'name')
            name.text = author.name
            country = ET.SubElement(root, 'country')
            country.text = author.country
            years = ET.SubElement(root, 'years', born=str(author.years.split('-')[0]),
                                  died=str(author.years.split('-')[1]))
            tree = ET.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            print(f'Данные автора {author.name} сохранены в файл {filename}.')

    def get_author_by_years(self, x, y):
        session = self.Session()
        authors = session.query(Author).filter(Author.years.split('-')[0].between(x, y)).all()
        for author in authors:
            print(author)
        session.close()

    def get_books_by_russian_authors(self):
        session = self.Session()
        books = session.query(Book).join(Author).filter(Author.country == 'Russia').all()
        for book in books:
            print(book)
        session.close()

    def get_books_by_pages(self, n):
        session = self.Session()
        books = session.query(Book).filter(Book.pages >= n).all()
        for book in books:
            print(book.title)
        session.close()

    def get_authors_by_books_count(self, n):
        session = self.Session()
        authors = session.query(Author).join(Book).group_by(Author).having(func.count(Book.id) > n).all()
        for author in authors:
            print(author.name)
        session.close()


def ex3():
    lib = Library()

    while True:
        choice = input('1 - Авторизация\n'
                       '2 - Регистрация\n'
                       '3 - Выход\n'
                       'Ваш выбор: ')
        if choice == '1':
            login = input('Введите ваш логин: ')
            password = input('Введите ваш пароль: ')
            if lib.login(login, password):
                print("Авторизация прошла успешно.")
                break
        elif choice == '2':
            login = input('Введите ваш логин: ')
            password = input('Введите ваш пароль: ')
            if lib.register(login, password):
                break
        elif choice == '3':
            exit(0)
        else:
            print('Вы ввели неправильное число.')

    while True:
        print('\n\nМеню')
        choice = input(
            '1 - Добавить автора вручную\n'
            '2 - Добавить автора через файл\n'
            '3 - Добавить книгу\n'
            '4 - Сохранить автора в json\n'
            '5 - Сохранить автора в xml\n'
            '6 - Вывести список авторов\n'
            '7 - Вывести список книг\n'
            '8 - Вывод фамилий всех авторов, родившихся в диапазоне между X и Y годами\n'
            '9 - Вывод всех книг, написанных авторами из России\n'
            '10 - Вывод всех книг с количеством страниц более N\n'
            '11 - Вывод всех авторов с числом книг более N\n'
            '0 - Выход \n'
            'Ваш выбор: ')
        if choice == '1':
            print('Добавление автора: ')
            name = input('Введите имя автора: ')
            country = input('Введите страну автора: ')
            years = input('Введите годы жизни автора через дефис (пример: 1965-2023): ')
            if lib.add_author(name, country, years):
                print('Автор успешно добавлен.')
        elif choice == '2':
            file = input('Введите путь к файлу с данными автора: ')
            author = lib.parse_author_file(file)
            if author is not None:
                res = lib.add_author(author.get('name', ''), author.get('country', ''), author.get('years', ''))
                if res:
                    print('Автор успешно добавлен.')

        elif choice == '3':
            print('Добавление книги')
            author_id = input('Введите id автора (Для получения id автора нажмите 7 в главном меню): ')
            title = input('Введите название книги: ')
            pages = input('Введите кол-во страниц книги: ')
            publisher = input('Введите издательство книги: ')
            year = input('Введите год издания книги: ')
            if lib.add_book(author_id, title, pages, publisher, year):
                print('Книга успешно добавлена.')
        elif choice == '4':
            author_id = input('Введите id автора для сохранения в json: ')
            lib.save_author_to_json(int(author_id))
        elif choice == '5':
            author_id = input('Введите id автора для сохранения в xml: ')
            lib.save_author_to_xml(int(author_id))
        elif choice == '6':
            lib.print_authors()
        elif choice == '7':
            lib.print_books()
        elif choice == '8':
            x = input('Введите первый год: ')
            y = input('Введите второй год: ')
            lib.get_author_by_years(int(x), int(y))
        elif choice == '9':
            lib.get_books_by_russian_authors()
        elif choice == '10':
            pages = input('Введите кол-во страниц: ')
            lib.get_books_by_pages(int(pages))
        elif choice == '11':
            books_cnt = input('Введите кол-во книг: ')
            lib.get_authors_by_books_count(int(books_cnt))
        elif choice == '0':
            exit(0)


if __name__ == '__main__':
    ex3()
