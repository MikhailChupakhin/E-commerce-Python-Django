# C:\Users\user1\PycharmProjects\IMSOUND\store\api\utils\exception_handler.py

from rest_framework.views import exception_handler
from rest_framework.response import Response
from api.utils.exceptions import Unauthorized


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    print(response)
    if isinstance(exc, Unauthorized):
        response.data['detail'] = 'Неправильные учетные данные'
    print()
    return response