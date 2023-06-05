from django.core import validators

class HexColorValidator(validators.RegexValidator):
    regex = r'^#([A-Fa-f0-9]{6})$'
    message = 'Введите цвет в HEX формате!'
