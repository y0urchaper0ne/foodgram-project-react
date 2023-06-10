from django.contrib import admin

from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
    )
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'
    model = User


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    list_filter = ('user', 'author',)
    empty_value_display = '-пусто-'
    model = Subscribe
