from apps.core.managers.abstract_manager import AbstractManager


class SeatManager(AbstractManager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)

    def get_by_session(self, session_id):
        return self.get_queryset().filter(session_id=session_id)