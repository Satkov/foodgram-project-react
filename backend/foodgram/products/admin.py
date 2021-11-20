from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, Product, Recipe, ShoppingCart,
                     Tag)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'get_followers')
    filter_horizontal = ('tags', 'ingredients')
    search_fields = ('name', 'author__username', 'tags__slug')

    def get_followers(self, obj):
        return FavoriteRecipe.objects.filter(recipes=obj).count()

    get_followers.short_description = 'Followers'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'get_unit', 'amount')
    search_fields = ('product__name',)

    def get_unit(self, obj):
        return obj.product.measurement_unit

    get_unit.short_description = 'Unit'
    get_unit.admin_order_field = 'product__measurement_unit'


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')


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
admin.site.register(FavoriteRecipe, FavoriteAdmin)
