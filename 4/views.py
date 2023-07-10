from zagmak_framework.templator import render
from patterns.creational_patterns import Engine, Logger

site = Engine()
logger = Logger('views')


def index_view(requests):
    return '200 OK', render('Elements/index.html', objects_list=site.genres)


def films_view(requests):
    logger.log('Films List')
    try:
        genre = site.find_genre_by_id(int(requests['requests_params']['id']))
        return '200 OK', render('Elements/films.html',
                                object_list=genre.films,
                                name=genre.name,
                                id=genre.id)
    except KeyError:
        return '200 OK', render('Elements/films.html',
                                object_list=site.films)
        return '200 OK', 'No films have been added yet'


class CreateFilmView:
    genre_id = -1

    def __call__(self, requests):
        if requests['method'] == 'POST':
            data = requests['data']
            name = site.decode_value(data['name'])
            genre = None
            if self.genre_id != -1:
                genre = site.find_genre_by_id(self.genre_id)
                film = site.create_film('translated', name, genre)
                site.films.append(film)
            return '200 OK', render('Elements/films.html',
                                    object_list=genre.films,
                                    name=genre.name,
                                    id=self.genre_id)
        else:
            try:
                self.genre_id = int(requests['requests_params']['id'])
                genre = site.find_genre_by_id(int(self.genre_id))

                return '200 OK', render('Elements/create_film.html',
                                        name=genre.name,
                                        id=genre.id)
            except KeyError:
                return '200 OK', 'No Genres have been added yet'


def genres_view(requests):
    return '200 OK', render('Elements/genre.html', objects_list=site.genres)


def create_genre_view(requests):
    if requests['method'] == 'POST':
        data = requests['data']
        name = data['name']
        name = site.decode_value(name)
        genre_id = data.get('genre_id')
        genre = None
        if genre_id:
            genre = site.find_genre_by_id(genre_id)

        new_genre = site.create_genre(name, genre)
        site.genres.append(new_genre)

        return '200 OK', render('Elements/index.html', objects_list=site.genres)
    else:
        genres = site.genres
        return '200 OK', render('Elements/create_genre.html',
                                genres=genres)

def copy_films(request):
    request_params = request['requests_params']

    try:
        name = request_params['name']
        film = site.find_film(name)
        if film:
            new_film = film.clone()
            new_film.name = f'copy{name}'
            site.films.append(new_film)

        return '200 OK', render('Elements/films.html',
                                object_list=site.films,
                                name=new_film.genre.name)
    except KeyError:
        return '200 OK', 'Film not found'


def not_found_404_view(requests):
    return '404 NOT FOUND', [b'This page is not found']
