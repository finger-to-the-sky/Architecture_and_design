from zagmak_framework.templator import render
from patterns.creational_patterns import Engine, Logger
from patterns.structural_patterns import Debug, AppRoute

site = Engine()
logger = Logger('views')
routes = {
}


@AppRoute(routes=routes, url='/')
class IndexView:
    @Debug(name='Index')
    def __call__(self, requests):
        return '200 OK', render('index.html', objects_list=site.genres)


@AppRoute(routes=routes, url='/films/')
class FilmsView:
    def __call__(self, requests):
        logger.log('Films List')
        try:
            genre = site.find_genre_by_id(int(requests['requests_params']['id']))
            return '200 OK', render('films/films.html',
                                    object_list=genre.films,
                                    name=genre.name,
                                    id=genre.id)
        except KeyError:
            return '200 OK', render('films/films.html',
                                    object_list=site.films)


@AppRoute(routes=routes, url='/create-film/')
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
            return '200 OK', render('films/films.html',
                                    object_list=genre.films,
                                    name=genre.name,
                                    id=self.genre_id)
        else:
            try:
                self.genre_id = int(requests['requests_params']['id'])
                genre = site.find_genre_by_id(int(self.genre_id))

                return '200 OK', render('films/create_film.html',
                                        name=genre.name,
                                        id=genre.id)
            except KeyError:
                return '200 OK', 'No Genres have been added yet'


@AppRoute(routes=routes, url='/genres/')
class GenresView:
    @Debug(name='Genres')
    def __call__(self, requests):
        return '200 OK', render('genres/genre.html', objects_list=site.genres)


@AppRoute(routes=routes, url='/create-genre/')
class CreateGenreView:
    def __call__(self, requests):
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

            return '200 OK', render('index.html', objects_list=site.genres)
        else:
            genres = site.genres
            return '200 OK', render('genres/create_genre.html',
                                    genres=genres)


@AppRoute(routes=routes, url='/copy-film/')
class CopyFilms:
    def __call__(self, requests):
        request_params = requests['requests_params']

        try:
            name = request_params['name']
            film = site.find_film(name)
            if film:
                new_film = film.clone()
                new_film.name = f'copy{name}'
                site.films.append(new_film)

            return '200 OK', render('films/films.html',
                                    object_list=site.films,
                                    name=new_film.genre.name)
        except KeyError:
            return '200 OK', 'Film not found'


class ErrorNotFound404:
    @Debug(name='ErrorNotFound404')
    def __call__(self, request):
        return '404 Error', '404 Page Not Found'


@AppRoute(routes=routes, url='/login/')
class LoginView:
    def __call__(self, request):
        return '200 OK', render('register/login.html')


@AppRoute(routes=routes, url='/register/')
class RegistrationView:
    def __call__(self, request):
        return '200 OK', render('register/registration.html')
