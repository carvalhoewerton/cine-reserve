from apps.core.managers.abstract_manager import AbstractManager


class MovieManager(AbstractManager):
    def list(self):
        return self.get_queryset().filter(sessions__active=True).distinct()