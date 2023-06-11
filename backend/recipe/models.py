from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models
from .validators import HexColorValidator

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название ингридиента'
        )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient')]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.TextField(
        unique=True,
        validators=[HexColorValidator()],
    )
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''Модель Рецепт'''
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        blank=False,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=255,
        blank=False,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='photos/',
        blank=False,
        verbose_name='Картинка'
    )
    text = models.TextField(
        verbose_name='Описание',
        blank=False,
        help_text='Введите текст описания'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        blank=False,
        verbose_name='Ингредиент',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        verbose_name='Тег'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        null=False,
        validators=[
            validators.MinValueValidator(
                1,
                message='Время приготовления не может быть меньше минуты'
            )
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return f'Рецепт: "{self.name}"'


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredient',
        on_delete=models.CASCADE,
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredient_recipe',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(
            1, message='Минимальное количество ингредиента - 1!')
        ],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент (кол-во)'
        verbose_name_plural = 'Ингредиенты (кол-во)'
        ordering = ('ingredient__name',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe')]

    def __str__(self):
        return (f'{self.ingredient.name} {self.amount}'
                f'{self.ingredient.measurement_unit}')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite_recipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в избранном',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('user', 'recipe')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe')]

    def __str__(self):
        return f'{self.user}, {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart',
        unique=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipe',
        verbose_name='Рецепт в корзине',
        unique=True,
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        ordering = ('user', 'recipe')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopping_cart')]

    def __str__(self):
        return f'{self.user}, {self.recipe}'
