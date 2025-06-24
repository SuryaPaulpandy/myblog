"""Django Modules"""

from typing import Any

from django.core.management.base import BaseCommand

from blog.models import Category


class Command(BaseCommand):
    """This Command is categories data"""

    help = " This commands inserts category data"

    def handle(self, *args: Any, **options):
        # Delete existing data
        Category.objects.all().delete()

        categories = ["Sports", "Technology", "Science", "Art", "Food"]

        for category_name in categories:
            Category.objects.create(name=category_name)

        self.stdout.write(self.style.SUCCESS("Completed inserting Data!"))
