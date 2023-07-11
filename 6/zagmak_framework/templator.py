from jinja2.environment import Environment
from jinja2 import FileSystemLoader
from .template_user_decorator import current_user_decorator


@current_user_decorator
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
