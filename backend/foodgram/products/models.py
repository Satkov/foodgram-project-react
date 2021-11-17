from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Product(models.Model):
    KILOGRAM = 'кг.'
    GRAM = 'г.'
    LITER = 'л.'
    MILLILITER = 'мл.'
    GLASS = 'ст.'
    TEASPOON = 'ч.л.'
    TABLESPOON = 'стл.л.'
    UNITS_CHOICES = [
        (KILOGRAM, 'киллограм'),
        (GRAM, 'грамм'),
        (LITER, 'литр'),
        (MILLILITER, 'миллилитр'),
        (GLASS, 'стакан'),
        (TEASPOON, 'чайная ложка'),
        (TABLESPOON, 'столовая ложка'),
    ]
    name = models.CharField(max_length=100, verbose_name='Название')
    measurement_unit = models.CharField(max_length=10, choices=UNITS_CHOICES,
                                        verbose_name='Единица измерения')

    class Meta:
        UniqueConstraint(fields=['name', 'measurement_unit'],
                         name='unique_product')
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    product = models.ForeignKey(Product, null=False, on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name='Количество')

    class Meta:
        UniqueConstraint(fields=['product', 'amount'],
                         name='unique_ingredients')
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.product.name


class Tag(models.Model):
    BLUE = '#34568B'
    CORAL = '#FF6F61'
    VIOLET = '#6B5B95'
    GREEN = '#88B04B'
    COLOR_CHOICES = [
        (BLUE, 'Blue'),
        (CORAL, 'Coral'),
        (VIOLET, 'Violet'),
        (GREEN, 'Green'),
    ]
    name = models.CharField(max_length=100, verbose_name='Название')
    color = models.CharField(max_length=100, choices=COLOR_CHOICES)
    slug = models.SlugField(verbose_name='Slug', max_length=30)

    class Meta:
        UniqueConstraint(fields=['name', 'color', 'slug'],
                         name='unique_tags')
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='recipes')
    name = models.CharField(max_length=100, verbose_name='Название',
                            null=False)
    image = models.ImageField(verbose_name="Картинка еды", upload_to='images')
    text = models.CharField(max_length=1000, verbose_name='Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         related_name='recipes')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.IntegerField(verbose_name='Время приготовления',
                                       null=False)
    pub_date = models.DateTimeField(verbose_name="Дата публикации",
                                    auto_now_add=True, db_index=True,
                                    null=False)

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, verbose_name='пользователь',
                             on_delete=models.CASCADE,
                             related_name='FavoriteRecipesUser')
    recipes = models.ManyToManyField(Recipe, blank=True,
                                     related_name='favorite_recipe')

    class Meta:
        UniqueConstraint(fields=['user', 'recipes'],
                         name='unique_favorite_recipe')
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, verbose_name='пользователь',
                             on_delete=models.CASCADE,
                             related_name='shoppingCartUser')
    cart = models.ManyToManyField(Recipe, blank=True,
                                  related_name='cart')

    class Meta:
        UniqueConstraint(fields=['user', 'cart'],
                         name='unique_cart')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
