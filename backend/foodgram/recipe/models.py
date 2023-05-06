from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingridients(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        blank=False,
        verbose_name='Название ингридиента'
        )
    quantity = models.IntegerField()
    measurement = models.CharField(
        max_length=20,
        verbose_name='Единица измерения',
    )


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.TextField(unique=True)
    slug = models.SlugField(unique=True)


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        help_text='Введите название блюда',
        max_length=200,
        blank=False,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipe/',
        blank=False,
        verbose_name='Картинка',
    )
    description = models.TextField(
        help_text='Добавьте описание рецепта',
        max_length=1000,
        blank=False,
        verbose_name='Описание рецепта',
    )
    ingridients= models.ForeignKey(
        Ingridients,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name='Ингридиенты',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name='Тэг',
    )
    time = models.IntegerField(
        verbose_name='Время приготовления',
        blank=False,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации')


    class Meta:
        ordering = ['-pub_date']