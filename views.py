from zagmak_framework.templator import render


def index_view(requests):
    return '200 OK', render('Elements/index.html', date=requests.get('date', None))


def elements_view(requests):
    return '200 OK', render('Elements/elements.html')


def not_found_404_view(requests):
    return '404 NOT FOUND', [b'This page is not found']
