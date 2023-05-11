import os.path
import sqlite3
import hashlib
import json
import xml.etree.ElementTree as ET
import re

class Library:
    def __init__(self, db_name="library.db"):
        self.db_name = db_name
        self.isLogged = False
        self.createTables()

    def createTables(self):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS Author (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    country TEXT,
                    years TEXT)
                ''')

        cur.execute('''
                    CREATE TABLE IF NOT EXISTS Book (
                    id INTEGER PRIMARY KEY,
                    author_id INTEGER,
                    title TEXT,
                    pages INTEGER,
                    publisher TEXT,
                    publication_year INTEGER,
                    FOREIGN KEY (author_id) REFERENCES Author (id))
                ''')

        cur.execute('''
                    CREATE TABLE IF NOT EXISTS DBUser (
                    id INTEGER PRIMARY KEY,
                    login TEXT,
                    password TEXT)
                ''')

        conn.commit()
        conn.close()

    def register_user(self, login, password):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cur.execute('SELECT COUNT(*) FROM DBUser WHERE login = ?', (login,))
        if cur.fetchone()[0] > 0:
            print('User with this login already exists')
            conn.close()
            return None

        hashed_password = hashlib.sha1(password.encode('utf-8')).hexdigest()
        cur.execute('INSERT INTO DBUser (login, password) VALUES (?, ?)', (login, hashed_password))

        conn.commit()
        conn.close()

    def login(self, login, password):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        hashed_passw = hashlib.sha1(password.encode('utf-8')).hexdigest()
        cur.execute('SELECT COUNT(*) FROM DBUser WHERE login = ? AND password = ?', (login, password))

        res = cur.fetchone()[0]
        conn.close()
        return False if res > 0 else True

    def add_author(self, name, country, years):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        if re.findall('\[[0-9]+, [0-9]+\]', str(years)):
            years = str(years).strip('[]').replace(', ', '-')

        print(f'Type: {type(years)} - {years}')
        cur.execute('INSERT INTO Author (name, country, years) VALUES (?, ?, ?)',
                    (name.strip(), str(country.strip()), years))

        conn.commit()
        conn.close()

    def ParseAuthorFromFile(self, filename):
        if not os.path.isfile(filename):
            print(f'File {filename} does not exist')
            return None

        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            print(f'File {filename} is empty')
            return None

        author_info = dict(line.strip().split(':', 1) for line in lines)

        author_name = author_info.get('name', '')
        if not author_name:
            print(f'File {filename} does not contain a "name" key or the value is empty')
            return None

        author_country = author_info.get('country', '')
        author_years = [int(year) for year in author_info.get('years', '').split('-') if year.isdigit()]

        if len(author_years) != 2:
            print(f'File {filename} does not contain a valid "years" key')
            return None

        author_dict = {
            'name': author_name,
            'country': author_country,
            'years': author_years
        }

        return author_dict

    def AddBook(self, author_id, title, pages, publisher, publication_year):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()

            if not all((author_id, title, pages, publisher, publication_year)):
                print('Заполните все поля')
                return False
            elif any((s.isspace() or s.isdigit() for s in (title, publisher))):
                print('Поля "Название" и "Издательство" не могут состоять только из пробелов и цифр')
                return False

            cur.execute('SELECT COUNT(*) FROM Author WHERE id = ?', (author_id,))
            if cur.fetchone()[0] == 0:
                print('Автора с таким id нет в базе данных')
                return False

            cur.execute('INSERT INTO Book (author_id, title, pages, publisher, publication_year) VALUES (?, ?, ?, ?, ?)',
                        (author_id, title, pages, publisher, publication_year))

            conn.commit()
            return True

    def getAuthors(self):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM Author')
            return cur.fetchall()

    def getBooks(self):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM Book')
            return cur.fetchall()

    def save_author_to_json(self, author_id):
        author = self._get_author_by_id(author_id)
        if not author:
            return False

        data = {
            'name': author['name'],
            'country': author['country'],
            'years': [int(y) for y in author['years']]
        }

        filename = f'{author["name"].replace(" ", "_")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        return True

    def save_author_to_xml(self, author_id):
        author = self._get_author_by_id(author_id)
        if not author:
            return False

        root = ET.Element('author')
        name = ET.SubElement(root, 'name')
        name.text = author['name']
        country = ET.SubElement(root, 'country')
        country.text = author['country']
        years = ET.SubElement(root, 'years', born=str(author['years'][0]), died=str(author['years'][1]))

        filename = f'{author["name"].replace(" ", "_")}.xml'
        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        return True

    def _get_author_by_id(self, author_id):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cur.execute('SELECT name, country, years FROM Author WHERE id = ?', (author_id,))
        row = cur.fetchone()

        conn.close()

        if row:
            return {'name': row[0], 'country': row[1], 'years': row[2].split('-')}
        else:
            return None

    def get_book(self, book_id):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM Book WHERE id = ?', (book_id,))
            return cur.fetchone()

    def get_author_name(self, author_id):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('SELECT name FROM Author WHERE id = ?', (author_id,))
            return cur.fetchone()[0]

    def get_book_author(self, book_id):
        book = self.get_book(book_id)
        if not book:
            return 'error', None
        author_id = book[1]
        author = self.get_author_name(author_id)
        return 'ok', author

    def print_authors(self):
        authors = self.getAuthors()
        print('ID   Name                 Country              Years')
        for author in authors:
            print(f'{author[0]:<5}{author[1]:<20}{author[2]:<20}{author[3]:<10}')
        print()

    def print_books(self):
        books = self.getBooks()
        print(
            'id   Author               Title                          Pages      Publisher           Publication Year')
        for book in books:
            author_name = self.get_author_name(book[1])
            print(f'{book[0]:<5}{author_name:<20}{book[2]:<30}{book[3]:<10}{book[4]:<20}{book[5]:<15}')
        print()

def ex2():
    library = Library()

    while True:
        print('1 - Login')
        print('2 - Register')
        print('3 - Exit')
        choice = input('Choice: ')

        if choice == '1':
            print('Login')
            login = input('Your Login: ')
            password = input('Your password: ')
            if library.login(login, password):
                print('Auth complete')
                break
        elif choice == '2':
            print('Registration')
            login = input('Enter your login: ')
            password = input('Enter your password: ')
            result = lib.register_user(login, password)
            if result is not None:
                break
        elif choice == '3':
            exit(0)
        else:
            print('Wrong number')

    while True:
        choice = input('1 - Добавить автора вручную\n2 - Добавить автора через файл\n3 - Добавить книгу\n4 - Сохранить автора в json\n5 - Сохранить автора в xml\n6 - Вывести список авторов\n7 - Вывести список книг\n8 - Выход \nВаш выбор: ')
        if choice   == '1':
            print('Добавление автора: ')
            name = input('Введите имя автора: ')
            country = input('Введите страну автора: ')
            years = input('Введите годы жизни автора через дефис (пример: 1965-2023): ')
            if library.add_author(name, country, years):
                print('Автор успешно добавлен.')
        elif choice == '2':
            file = input('Введите путь к файлу с данными автора: ')
            author = library.parse_author_file(file)
            if author is not None:
                res = library.add_author(author.get('name', ''), author.get('country', ''), author.get('years', ''))
                if res:
                    print('Автор успешно добавлен.')

        elif choice == '3':
            print('Добавление книги')
            author_id = input('Введите id автора (Для получения id автора нажмите 8 в главном меню): ')
            title = input('Введите название книги: ')
            pages = input('Введите кол-во страниц книги: ')
            publisher = input('Введите издательство книги: ')
            year = input('Введите год издания книги: ')
            if library.AddBook(author_id, title, pages, publisher, year):
                print('Книга успешно добавлена.')
        elif choice == '4':
            author_id = input('Введите id автора для сохранения в json: ')
            library.save_author_to_json(int(author_id))
        elif choice == '5':
            author_id = input('Введите id автора для сохранения в xml: ')
            library.save_author_to_xml(int(author_id))
        elif choice == '6':
            library.print_authors()
        elif choice == '7':
            library.print_books()
        elif choice == '8':
            exit(0)


if __name__ == '__main__':
    ex2()
