from patterns.creational_patterns import Engine


def current_user_decorator(func):
    def wrapper(*args, **kwargs):
        kwargs['current_user'] = Engine.current_user
        return func(*args, **kwargs)

    return wrapper
