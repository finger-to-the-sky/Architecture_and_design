from datetime import date
from wsgiref.simple_server import make_server

from urls import routes
from zagmak_framework.main import Framework


def date_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [date_front, other_front]

application = Framework(routes=routes, fronts=fronts)

with make_server('', 8000, application) as httpd:
    print('Server has been running on: http://localhost:8000/')
    httpd.serve_forever()
