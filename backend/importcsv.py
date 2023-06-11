from csv import reader

from django.core.management.base import BaseCommand
from recipe.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients data from csv-file to DB.'

    def handle(self, *args, **kwargs):
        with open(
                'recipes/data/ingredients.csv', 'r',
                encoding='UTF-8'
        ) as ingredients:
            for row in reader(ingredients):
                if len(row) == 2:
                    if not Ingredient.objects.filter(
                        name=row[0], measurement_unit=row[1],
                    ).exists():
                        Ingredient.objects.get_or_create(
                            name=row[0], measurement_unit=row[1],
                        )
