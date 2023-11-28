from copy import deepcopy
from quopri import decodestring
from .behavioral_patterns import Subject, FileWriter
from zagmak_framework.templator import render
from .unit_of_work import DomainObject
from sqlite3 import connect


# Так как пользователи не будут иметь типы, потому что все, что они будут делать
# на киносайте - это комментировать и оценивать фильмы, создаем обычный класс.
class User(DomainObject):
    """
    Usual User class for login and Registration
    """

    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.channels = []


# Prototype method
class FilmPrototype:

    def clone(self):
        return deepcopy(self)


class Film(FilmPrototype, Subject):

    def __init__(self, name, genre):
        self.name = name
        self.genre = genre
        self.genre.films.append(self)
        self.users = []
        super().__init__()

    def add_subscribers(self, subscriber: User):
        self.users.append(subscriber)
        subscriber.channels.append(self)
        self.notify()


class OriginalFilm(Film):
    pass


class TranslateFilm(Film):
    pass


class FilmFactory:
    types = {
        'original': OriginalFilm,
        'translated': TranslateFilm
    }

    # Factory method
    @classmethod
    def create(cls, type_, name, genre):
        return cls.types[type_](name, genre)


class Genre:
    auto_id = 0

    def __init__(self, name, genre):
        self.id = Genre.auto_id
        Genre.auto_id += 1
        self.name = name
        self.genre = genre
        self.films = []

    def films_count(self):
        count = len(self.films)
        if self.genre:
            count += self.genre.films_count()
        return count


# Main Interface
class Engine:
    def __init__(self):
        self.films = []
        self.genres = []
        self.users = []

    @staticmethod
    def create_genre(name, genre=None):
        return Genre(name, genre)

    def find_genre_by_id(self, id):
        for genre in self.genres:
            if genre.id == id:
                return genre
        raise Exception(f'Genre Not found with id: {id} ')

    @staticmethod
    def create_film(type_, name, genre):
        return FilmFactory.create(type_, name, genre)

    def find_film(self, name):
        for film in self.films:
            if film.name == name:
                return film
        return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')

    @staticmethod
    def create_user(id, username, email, password):
        return User(id=id, username=username, email=email, password=password)

    def get_user(self, name):
        for user in self.users:
            if user.username == name:
                return user


class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name, writer=FileWriter):
        self.name = name
        self.writer = writer(self.name)

    def log(self, text):
        text = f'log---> {text}'
        self.writer.write(text)


class UserMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'users'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, username, email, password = item
            user = User(id, username, email, password)
            result.append(user)
        return result

    def find_by_id(self, id):
        statement = f'SELECT id, username FROM {self.tablename} WHERE id=?'
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return User(*result)
        else:
            raise RecordNotFoundException(f'recoder with id={id} not found')

    def insert(self, obj):
        statement = f'INSERT INTO {self.tablename} (username, email, password) VALUES (?, ?, ?)'
        self.cursor.execute(statement, (obj.username, obj.email, obj.password))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f'UPDATE {self.tablename} SET username? WHERE id=?'

        self.cursor.execute(statement, (obj.username, obj.id))
        try:
            self.cursor.execute(statement, (obj.username, obj.id))
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f'DELETE FROM {self.tablename} WHERE id=?'
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


connection = connect('patterns.sqlite')


class MapperRegistry:
    mappers = {
        'users': UserMapper,
        # 'films': FilmMapper,
    }

    @staticmethod
    def get_mapper(obj):
        return UserMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')
