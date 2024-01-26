from sentry_sdk import capture_exception


#  Определиться с тем, какие урлы трекаем
#  Передалать асинхронно
#  Селери?
class SentryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code in [403, 404] or response.status_code >= 500:
            capture_exception(Exception(f"HTTP {response.status_code} Error"))
        return response


class XCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Проверяем, если ответ кэширован
        if response.has_header('Cache-Control') and 'max-age' in response['Cache-Control']:
            response['X-Cache'] = 'hit'
        else:
            response['X-Cache'] = 'miss'

        return response
