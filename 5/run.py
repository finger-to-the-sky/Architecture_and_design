from wsgiref.simple_server import make_server
from urls import fronts
from views import routes
from zagmak_framework.main import Framework

application = Framework(routes=routes, fronts=fronts)

with make_server('', 8000, application) as httpd:
    for route in routes:
        print(f'http://localhost:8000{route}')
    httpd.serve_forever()
