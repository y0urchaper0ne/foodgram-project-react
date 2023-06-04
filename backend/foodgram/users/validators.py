import re

from django.core.exceptions import ValidationError


def username_validator(value):
    if value.lower() == 'me':
        raise ValidationError('Имя пользователя не может быть me')
    if not re.match(r'^[a-zA-Z0-9_.]+$', value):
        raise ValidationError(
            f'Имя пользователя {value} содержит недопустимые символы'
        )
