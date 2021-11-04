import django_filters

from .models import Recipe


class RecipesFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(
        field_name='tags__slug',
    )
    author = django_filters.NumberFilter(
        field_name='author__id'
    )
    # is_favorited = django_filters.BooleanFilter(
    #     field_name='favorite_recipe__recipe',
    #     method='filter_is_favorited',
    #     lookup_expr='isnull'
    # )

    # def filter_is_favorited(self, queryset, name, value):
    #     lookup = '__'.join([name, 'isnull'])
    #     user = self.request.user
    #     user_recipes = user.Recipe.all()
    #     user_recipes_id = [i.recipe.id for i in user_recipes]
    #     return queryset.filter(id__in=user_recipes_id, **{lookup: not (value)})

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
