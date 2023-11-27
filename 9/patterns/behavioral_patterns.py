from jsonpickle import dumps, loads
from zagmak_framework.templator import render


class Observer:

    def update(self, subject):
        pass


class Subject:

    def __init__(self):
        self.observers = []

    def notify(self):
        for obs in self.observers:
            obs.update(self)


class EmailNotifier(Observer):
    def update(self, subject):
        print('EMAIL: ', 'Новинка: ', subject.users[-1].channels[-1].name)
        pass


# Template method
class TemplateView:
    template_name = 'template.html'

    def get_context_data(self):
        return {}

    def get_template(self):
        return self.template_name

    def render_template(self):
        template_name = self.get_template()
        context = self.get_context_data()
        return '200 OK', render(template_name, **context)

    def __call__(self, request):
        return self.render_template()


class ListView(TemplateView):
    queryset = []
    template_name = 'list.html'
    context = 'objects_list'

    def get_queryset(self):
        print(self.queryset)
        return self.queryset

    def get_context_object_name(self):
        return self.context

    def get_context_data(self):
        queryset = self.get_queryset()
        context_object_name = self.get_context_object_name()
        context = {context_object_name: queryset}
        return context


# class CreateView(TemplateView):
#     template_name = 'create.html'
#
#     @staticmethod
#     def get_request_data(request):
#         return request['data']
#
#     def create_obj(self, data):
#         pass
#
#     def __call__(self, request):
#         if request['method'] == 'POST':
#             data = self.get_request_data(request)
#             self.create_obj(data)
#             return self.render_template()
#         else:
#             return super().__call__(request)


class BaseSerializer:

    def __init__(self, obj):
        self.obj = obj

    def save(self):
        return dumps(self.obj)

    @staticmethod
    def load(data):
        return loads(data)


# Strategy
class ConsoleWriter:

    def write(self, text):
        print(text)


class FileWriter:
    def __init__(self, filename):
        self.filename = filename

    def write(self, text):
        with open(self.filename, 'a', encoding='UTF-8') as file:
            file.write(f'{text}\n')
