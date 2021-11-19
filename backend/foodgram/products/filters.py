import django_filters

from .models import FavoriteRecipe, Product, Recipe, ShoppingCart, Tag


class RecipesFilter(django_filters.FilterSet):
    tags = django_filters.filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
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
        if user.is_anonymous:
            return queryset.none()
        shopping_cart, created = ShoppingCart.objects.get_or_create(user=user)
        user_recipes_id = shopping_cart.cart.values_list('id', flat=True)
        return queryset.filter(id__in=user_recipes_id)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none()
        user_recipes, created = FavoriteRecipe.objects.get_or_create(user=user)
        user_recipes_id = user_recipes.recipes.values_list('id', flat=True)
        return queryset.filter(id__in=user_recipes_id)

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='contains'
    )

    class Meta:
        model = Product
        fields = ['name']
