from copy import deepcopy
from quopri import decodestring
from .behavioral_patterns import Subject, FileWriter
from zagmak_framework.templator import render


# Так как пользователи не будут иметь типы, потому что все, что они будут делать
# на киносайте - это комментировать и оценивать фильмы, создаем обычный класс.
class User:
    """
    Usual User class for login and Registration
    """

    def __init__(self, username, email, password):
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
    def create_user(username, email, password):
        return User(username=username, email=email, password=password)

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