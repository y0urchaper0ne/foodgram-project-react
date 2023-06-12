from django.contrib import admin
from django.contrib.admin import display
from .models import (Recipe, Ingredient, Tag, Favorite,
                     ShoppingСart, RecipeIngredients,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit',
    )
    list_filter = ('name',)
    empty_value_display = '-пусто-'
    model = Ingredient


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'
    model = Tag


class IngredientInline(admin.StackedInline):
    model = RecipeIngredients


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'favorite_amount',)
    list_filter = ('name', 'author', 'tags',)
    model = Recipe
    inlines = [IngredientInline,]

    @display(description = 'Добавлено в избранное',
             empty_value='Не добавлено в избранное')
    def favorite_amount(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    empty_value_display = '-пусто-'
    model = Favorite


@admin.register(ShoppingСart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('user', 'recipe',)
    empty_value_display = '-пусто-'
    model = ShoppingСart


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    empty_value_display = '-пусто-'
    model = RecipeIngredients
