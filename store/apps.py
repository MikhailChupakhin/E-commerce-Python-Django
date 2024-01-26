from django.apps import AppConfig

from .tasks import orders_alert_bot  # Импортируйте задачу запуска бота


class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'your_app_name'

    def ready(self):
        try:
            orders_alert_bot(repeat=3600)
            print('orders_alert_bot STARTED.')
        except:
            print('orders_alert_bot FAILED.')