from django.contrib import admin
from .models import Ingredient, Tag, Recipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'image', 'text',
                    'time_to_cook', 'pub_date')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'units')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)