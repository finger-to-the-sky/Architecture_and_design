from views import not_found_404_view
from quopri import decodestring
from .http_processor import RequestGet, RequestPost


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

        if not path.endswith('/'):
            path = f'{path}/'

        request = {}

        method = environ['REQUEST_METHOD']
        request['method'] = method
        # print(environ)
        if method == 'POST':
            data = RequestPost().get_request_params(environ)
            request['data'] = Framework.decode_value(data)
            print(f'Нам пришёл post-запрос: {Framework.decode_value(data)}')

        if method == 'GET':
            request_params = RequestGet().get_request_params(environ)
            request['request_params'] = Framework.decode_value(request_params)
            if Framework.decode_value(request_params) != {}:
                print(f'Нам пришли GET-параметры:'
                      f' {Framework.decode_value(request_params)}')

        if path in self.routes:
            view = self.routes[path]
        else:
            view = not_found_404_view

        for front in self.fronts:
            front(request)

        code, body = view(request)
        start_response(code, [('Content-Type', 'text.html')])
        return [str(body).encode('utf-8')]

    @staticmethod
    def decode_value(data):
        new_data = {}
        for k, v in data.items():
            val = bytes(v.replace('%', '=').replace("+", " "), 'UTF-8')
            val_decode_str = decodestring(val).decode('UTF-8')
            new_data[k] = val_decode_str
        return new_data
