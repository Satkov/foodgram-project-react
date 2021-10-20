from django.contrib import admin
from .models import Ingredient, Tag, Recipe, Product


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'text',
                    'cooking_time', 'pub_date')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'Recipe', 'amount')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Product, ProductAdmin)