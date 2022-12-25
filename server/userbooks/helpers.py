from userbooks.models import UserBookSession


def check_unfinished_session(book_id: int):
    userbook_session = UserBookSession.objects.filter(userbook__pk=book_id)

    if userbook_session.exists():
        not_finished_sessions = userbook_session.filter(finished_at=None).order_by('-created_at')

        if not_finished_sessions.exists():
            return not_finished_sessions.first()

        return None
