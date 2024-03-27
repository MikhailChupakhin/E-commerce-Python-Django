from django.http import HttpResponsePermanentRedirect

from seo_manager.models import Redirect


'''Off(currently isnt nessesary)'''
# class RedirectMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         response = self.get_response(request)
#         old_path = request.path_info
#
#         try:
#             redirect_obj = Redirect.objects.get(old_path=old_path)
#             return HttpResponsePermanentRedirect(redirect_obj.new_path)
#         except Redirect.DoesNotExist:
#             pass
#
#         return response


class CustomHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':

            request.META['HTTP_ACCESS_CONTROL_REQUEST_HEADERS'] = 'PaginationParam'

        response = self.get_response(request)
        return response