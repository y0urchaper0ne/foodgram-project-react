from django.contrib import admin
from .models import (Recipe, Ingredient, Tag, Favorite,
                     ShoppingCart, RecipeIngredients,)


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
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


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author',
    )
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'
    model = Recipe


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    empty_value_display = '-пусто-'
    model = Favorite


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('user', 'recipe',)
    empty_value_display = '-пусто-'
    model = ShoppingCart


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients', 'amount')
    empty_value_display = '-пусто-'
    model = RecipeIngredients
