from django.core.management.base import BaseCommand
from store.models import Product

class Command(BaseCommand):
    help = "Seed sample products"

    def handle(self, *args, **options):
        if Product.objects.exists():
            self.stdout.write(self.style.WARNING("Products already exist. Skipping."))
            return
        data = [
            dict(name='Wireless Mouse', description='Ergonomic wireless mouse', price=24.99,
                 image_url='https://picsum.photos/seed/mouse/400/240', category='Electronics'),
            dict(name='Mechanical Keyboard', description='RGB mechanical keyboard', price=79.99,
                 image_url='https://picsum.photos/seed/keyboard/400/240', category='Electronics'),
            dict(name='Water Bottle', description='Insulated stainless steel bottle', price=19.99,
                 image_url='https://picsum.photos/seed/bottle/400/240', category='Home'),
            dict(name='Notebook', description='Hardcover ruled notebook', price=9.99,
                 image_url='https://picsum.photos/seed/notebook/400/240', category='Stationery'),
        ]
        Product.objects.bulk_create([Product(**d) for d in data])
        self.stdout.write(self.style.SUCCESS("Seeded products."))
