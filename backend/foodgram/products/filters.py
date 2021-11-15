import django_filters

from .models import Recipe, FavoriteRecipes, ShoppingCart, Product


class RecipesFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(
        field_name='tags__slug',
    )
    author = django_filters.NumberFilter(
        field_name='author__id'
    )
    is_favorited = django_filters.BooleanFilter(
        field_name='favorite_recipe__recipes',
        method='filter_is_favorited',
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='cart__cart',
        method='filter_is_in_shopping_cart',
    )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        user_recipes, created = ShoppingCart.objects.get_or_create(user=user)
        user_recipes_id = [i.id for i in user_recipes.cart.all()]
        return queryset.filter(id__in=user_recipes_id)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        user_recipes, created = FavoriteRecipes.objects.get_or_create(user=user)
        user_recipes_id = [i.id for i in user_recipes.recipes.all()]
        return queryset.filter(id__in=user_recipes_id)

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        method='get_ingredient__name'
    )

    def get_ingredient__name(self, queryset, name, value):
        return queryset.filter(name__contains=value)

    class Meta:
        model = Product
        fields = ['name']
