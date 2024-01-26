from django.contrib.sessions.models import Session
from django.utils import timezone

from products.models import ComparisonList

from .celery import app


@app.task
def clear_expired_sessions():

    current_time = timezone.localtime()

    # Получение количества сессий до удаления
    initial_count = Session.objects.count()

    # Очистка истекших сессий
    expired_sessions = Session.objects.filter(expire_date__lt=current_time)

    # Удаление связанных ComparisonList у истекших сессий
    for session in expired_sessions:
        try:
            comparison_list = ComparisonList.objects.get(session=session)
            comparison_list.delete()
        except ComparisonList.DoesNotExist:
            pass

    # Удаление сессий
    deleted_count = expired_sessions.delete()[0]

    # Получение количества сессий после удаления
    remaining_count = Session.objects.count()

    return f'Было сессий:{initial_count}. Удалено {deleted_count} истекших сессий. Осталось {remaining_count} сессий.'

