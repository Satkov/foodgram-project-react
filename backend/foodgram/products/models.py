from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Product(models.Model):
    UNITS_CHOICES = [
        ('кг.', 'киллограм'),
        ('г.', 'грамм'),
        ('л.', 'литр'),
        ('мл.', 'миллилитр'),
        ('ст.', 'стакан'),
        ('ч.л.', 'чайная ложка'),
        ('стл.л.', 'столовая ложка'),
    ]
    name = models.CharField(max_length=100, verbose_name='Название')
    measurement_unit = models.CharField(max_length=10, choices=UNITS_CHOICES)
    unique_together = [['name', 'measurement_unit']]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.ForeignKey(Product, null=False, on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name='Количество')


class Tag(models.Model):
    COLOR_CHOICES = [
        ('#34568B', 'Blue'),
        ('#FF6F61', 'Coral'),
        ('#6B5B95', 'Violet'),
        ('#88B04B', 'Green'),
    ]
    name = models.CharField(max_length=100, verbose_name='Название')
    color = models.CharField(max_length=100, choices=COLOR_CHOICES)
    slug = models.SlugField(verbose_name='Slug', max_length=30)


class Recipe(models.Model):
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='author', null=False)
    name = models.CharField(max_length=100, verbose_name='Название', null=False)
    image = models.ImageField(verbose_name="Картинка еды", upload_to='images')
    text = models.CharField(max_length=1000, verbose_name='Описание')
    ingredients = models.ManyToManyField(Ingredient, blank=False,
                                         related_name='Recipe')
    tags = models.ManyToManyField(Tag, blank=False)
    cooking_time = models.IntegerField(verbose_name='Время приготовления', null=False)
    pub_date = models.DateTimeField(verbose_name="Дата публикации",
                                    auto_now_add=True, db_index=True, null=False)


class FavoriteRecipes(models.Model):
    user = models.ForeignKey(User, verbose_name='пользователь',
                             on_delete=models.CASCADE,
                             related_name='FavoriteRecipesUser')
    recipes = models.ForeignKey(Recipe, verbose_name='Избранное',
                                on_delete=models.CASCADE,
                                related_name='Recipe')


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, verbose_name='пользователь',
                             on_delete=models.CASCADE,
                             related_name='ShoppingCartUser')
    cart = models.ForeignKey(Recipe, verbose_name='Корзина',
                             on_delete=models.CASCADE,
                             related_name='Cart')
