# C:\Users\user1\PycharmProjects\IMSOUND\store\api\exceptions.py

from rest_framework.exceptions import APIException


class Unauthorized(APIException):
    status_code = 401
    default_detail = 'Unauthorized'
    default_code = 'unauthorized'