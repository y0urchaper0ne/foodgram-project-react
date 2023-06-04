# Generated by Django 3.2.18 on 2023-05-21 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0004_auto_20230520_1319'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredients',
            options={'verbose_name': 'Ингридиент', 'verbose_name_plural': 'Ингридиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-pub_date'], 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'Тэг', 'verbose_name_plural': 'Тэги'},
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='tag',
            new_name='tags',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='description',
            new_name='text',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='time',
        ),
        migrations.AddField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(default=1, verbose_name='Время приготовления (в минутах)'),
            preserve_default=False,
        ),
    ]
