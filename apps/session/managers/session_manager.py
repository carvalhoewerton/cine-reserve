from apps.core.managers.abstract_manager import AbstractManager


class SessionManager(AbstractManager):

    def get_by_movie(self, movie_id):
        return self.get_queryset().filter(movie_id=movie_id)