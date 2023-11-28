from datetime import date


def date_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [date_front, other_front]

