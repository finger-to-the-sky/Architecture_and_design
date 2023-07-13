from jinja2.environment import Environment
from jinja2 import FileSystemLoader
# from .template_user_decorator import current_user_decorator


class CurrentUserDecorator:
    current_user = 'Guest'

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        kwargs['current_user'] = self.current_user
        return self.func(*args, **kwargs)


@CurrentUserDecorator
def render(template_name, folder='templates', **kwargs):
    """

    :param template_name:
    :param folder:
    :param kwargs:
    :return:
    """
    env = Environment()
    env.loader = FileSystemLoader(folder)
    template = env.get_template(template_name)
    return template.render(**kwargs)
