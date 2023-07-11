from copy import deepcopy
from quopri import decodestring


# Prototype method
class FilmPrototype:

    def clone(self):
        return deepcopy(self)


class Film(FilmPrototype):

    def __init__(self, name, genre):
        self.name = name
        self.genre = genre
        self.genre.films.append(self)


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

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('INFO:', text)
