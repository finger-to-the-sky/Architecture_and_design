from views import not_found_404_view


class Framework:
    def __init__(self, routes, fronts):
        self.routes = routes
        self.fronts = fronts

    def __call__(self, environ, start_response):
        """
        :param environ: словарь данных от сервера
        :param start_response: функция для ответа серверу
        """

        path = environ['PATH_INFO']
        if path in self.routes:
            view = self.routes[path]
        else:
            view = not_found_404_view

        if not path.endswith('/'):
            path = f'{path}/'

        requests = {}
        for front in self.fronts:
            front(requests)

        code, body = view(requests)
        start_response(code, [('Content-Type', 'text.html')])

        return [str(body).encode('utf-8')]
