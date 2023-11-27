from zagmak_framework.templator import render, CurrentUserDecorator
from patterns.creational_patterns import Engine, Logger, MapperRegistry
from patterns.structural_patterns import Debug, AppRoute
from patterns.behavioral_patterns import ListView, EmailNotifier, BaseSerializer
from patterns.unit_of_work import UnitOfWork

site = Engine()
logger = Logger('views')
email_notifier = EmailNotifier()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)

routes = {}


@AppRoute(routes=routes, url='/')
class IndexView:
    @Debug(name='Index')
    def __call__(self, requests):
        logger.log('Index')
        return '200 OK', render('index.html', objects_list=site.genres)


@AppRoute(routes=routes, url='/films-list/')
class FilmsListView:
    def __call__(self, requests):
        logger.log('Films List')
        try:
            genre = site.find_genre_by_id(int(requests['requests_params']['id']))
            return '200 OK', render('films/films_list.html',
                                    objects_list=genre.films,
                                    name=genre.name,
                                    id=genre.id)
        except KeyError:
            return '200 OK', render('films/films_list.html',
                                    objects_list=site.films)


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
                film.observers.append(email_notifier)
                try:

                    user = site.get_user(CurrentUserDecorator.current_user)
                    film.add_subscribers(user)
                    site.films.append(film)

                    return '200 OK', render('films/films_list.html',
                                            objects_list=genre.films,
                                            name=genre.name,
                                            id=self.genre_id)
                except Exception:
                    return '404 Error', 'You Need Authorization of admin user.'
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

            return '200 OK', render('films/films_list.html',
                                    objects_list=site.films,
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
        logger.log('Login')
        if request['method'] == 'POST':
            data = request['data']
            email, password = site.decode_value(data['email']), site.decode_value(data['password'])
            mapper = MapperRegistry.get_current_mapper('users')
            users_list = mapper.all()
            for user in users_list:
                if user.email == email and user.password == password:
                    print(f'Пользователь {user.username} авторизован!')
                    CurrentUserDecorator.current_user = user.username
                    return '200 OK', render('index.html')
                else:
                    return '200 OK', render('register/login.html', error='Неверный Email или Password')
        else:
            return '200 OK', render('register/login.html')


@AppRoute(routes=routes, url='/register/')
class RegistrationView:
    user_id = 0

    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            username, email, password, confirm_password = \
                site.decode_value(data['username']), \
                    site.decode_value(data['email']), \
                    site.decode_value(data['password']), \
                    site.decode_value(data['confirm-password'])

            if password == confirm_password:
                self.user_id = self.user_id + 1
                new_user = site.create_user(id=self.user_id, username=username, email=email, password=password)
                site.users.append(new_user)
                new_user.mark_new()
                UnitOfWork.get_current().commit()
                print(f'Пользователь № {site.users.index(site.users[-1])} '
                      f'с ником {username} успешно зарегистрирован!')

                return '201 OK', render('register/login.html')
            else:
                return '200 OK', render('register/registration.html', error='Пароли не совпадают!')
        else:
            return '200 OK', render('register/registration.html')


@AppRoute(routes=routes, url='/logout/')
class LogoutView:
    def __call__(self, request):
        CurrentUserDecorator.current_user = 'Guest'
        return '200 OK', render('index.html', objects_list=site.genres)


# Данный список нет смысла делать общедоступным, так как это не платформа общения людей между собой,
# поэтому в шаблоне я ограничу доступ только для пользователя с ником Admin или admin.
@AppRoute(routes=routes, url='/users-list/')
class UsersListView(ListView):
    template_name = 'users/user_list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('users')
        return mapper.all()


@AppRoute(routes=routes, url='/film/')
class FilmView:

    def __call__(self, request):
        request_params = request['requests_params']

        try:
            name = request_params['name']
            film = site.find_film(name)
            if film:
                return render('films/film.html', name=name)
        except KeyError:
            return 'Film Not Found'


@AppRoute(routes=routes, url='/api/')
class FilmApi:
    @Debug(name='FilmApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.films).save()
