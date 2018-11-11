from django.apps import AppConfig


class UsersAppConfig(AppConfig):

    name = "pizzeria_dangelo.users"
    verbose_name = "Users"

    def ready(self):
        try:
            import users.signals  # noqa F401 pylint: disable=unused-variable
        except ImportError:
            pass
