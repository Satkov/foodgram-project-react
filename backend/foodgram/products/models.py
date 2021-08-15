from django.db import models
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    UNITS_CHOICES = [
        ('кг.', 'киллограм'),
        ('гр.', 'грамм'),
        ('л.', 'литр'),
        ('мл.', 'миллилитр'),
        ('ст.', 'стакан'),
        ('ч.л.', 'чайная ложка'),
        ('стл.л.', 'столовая ложка'),
    ]

    name = models.CharField(max_length=100, verbose_name='Название')
    amount = models.IntegerField(verbose_name='Количество')
    Units = models.CharField(choices=UNITS_CHOICES)


class Tag(models.Model):
    COLOR_CHOICES = [
        ('#34568B', 'Blue'),
        ('#FF6F61', 'Coral'),
        ('#6B5B95', 'Violet'),
        ('#88B04B', 'Green'),
    ]
    name = models.CharField(max_length=100, verbose_name='Название')
    color = ColorField(choices=COLOR_CHOICES)
    slug = models.SlugField(verbose_name='Slug', max_length=30)


class Recipe(models.Model):
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='Recipe')
    name = models.CharField(max_length=100, verbose_name='Название')
    image = models.ImageField(upload_to='images')
    text = models.CharField(max_length=1000, verbose_name='Описание')
    ingredients = models.ManyToManyField(Ingredient)
    tag = models.ManyToManyField(Tag)
    time_to_cook = models.IntegerField(verbose_name='Время приготовления')