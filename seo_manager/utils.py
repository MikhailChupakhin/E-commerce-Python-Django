from django.core.exceptions import ObjectDoesNotExist

from seo_manager.models import Redirect


# Создание редиректов, с предотвращением циклических
def create_redirect(old_path, new_path):
    try:
        reverse_redirect = Redirect.objects.get(old_path=new_path)
        if reverse_redirect.new_path == old_path:
            reverse_redirect.delete()
    except ObjectDoesNotExist:
        pass
    Redirect.objects.create(old_path=old_path, new_path=new_path)