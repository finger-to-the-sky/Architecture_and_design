from wsgiref.simple_server import make_server
from urls import fronts
from views import routes
from zagmak_framework.main import Framework

application = Framework(routes=routes, fronts=fronts)

HOST = 'localhost'
PORT = 8000

with make_server(HOST, PORT, application) as httpd:
    for route in routes:
        print(f'http://{HOST}:{PORT}{route}')
    httpd.serve_forever()
