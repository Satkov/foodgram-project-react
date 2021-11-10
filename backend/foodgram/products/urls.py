
from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import RecipeViewSet, TagViewSet, IngredientViewSet, FavoriteApiView, FollowViewSet

router = DefaultRouter()

router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'users/subscriptions', FollowViewSet)
router.register(r'users', FollowViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:recipe_id>/favorite/', FavoriteApiView.as_view()),
]

