from django.core.management.base import BaseCommand
from products.models import ProductSubCategory


class Command(BaseCommand):
    help = 'Resave all PSC items in DB'

    def handle(self, *args, **options):
        all_subcategories = ProductSubCategory.objects.all()
        for subcategory in all_subcategories:
            subcategory.save()
        self.stdout.write(self.style.SUCCESS('Success.'))