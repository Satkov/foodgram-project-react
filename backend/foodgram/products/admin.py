from django.contrib import admin
from .models import (Ingredient, Tag, Recipe,
                     Product, FavoriteRecipes,
                     ShoppingCart)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name')
    filter_horizontal = ('tags', 'ingredients')
    search_fields = ('name', 'author__username', 'tags__slug')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_unit', 'amount')

    def get_unit(self, obj):
        return obj.name.measurement_unit

    get_unit.short_description = 'Unit'
    get_unit.admin_order_field = 'name__measurement_unit'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class FavoriteAdmin(admin.ModelAdmin):
    filter_horizontal = ('recipes',)
    list_display = ('user',)


class ShoppingCartAdmin(admin.ModelAdmin):
    filter_horizontal = ('cart',)
    list_display = ('user',)


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(FavoriteRecipes, FavoriteAdmin)
