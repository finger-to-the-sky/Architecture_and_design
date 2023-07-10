from views import index_view, copy_films,films_view, genres_view, CreateFilmView, create_genre_view

routes = {
    '/': index_view,
    '/films/': films_view,
    '/genres/': genres_view,
    '/create-genre/': create_genre_view,
    '/create-film/': CreateFilmView(),
    '/copy-film/': copy_films
}

