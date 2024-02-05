from rest_framework.response import Response
from rest_framework import status
from django_redis import get_redis_connection
import json


def gt_check_get_cached_basket(request):
    guest_token = request.headers.get('guest-token')
    if not guest_token:
        return None, Response({'message': 'Отсутствует guest_token в заголовках запроса.'},
                            status=status.HTTP_400_BAD_REQUEST)

    redis_connection = get_redis_connection("default")

    basket_data = redis_connection.get(guest_token)

    if basket_data:
        basket_data = json.loads(basket_data)
    else:
        basket_data = {}

    return guest_token, redis_connection, basket_data