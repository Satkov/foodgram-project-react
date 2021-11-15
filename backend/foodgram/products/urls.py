from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import (RecipeViewSet, TagViewSet, IngredientViewSet,
                    FavoriteViewSet, FollowViewSet, DownloadShoppingList,
                    ShoppingCartViewSet)

router = DefaultRouter()

router.register(r'recipes', RecipeViewSet)
router.register(r'recipes', ShoppingCartViewSet)
router.register(r'recipes', FavoriteViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'users/subscriptions', FollowViewSet)
router.register(r'users', FollowViewSet)

urlpatterns = [
    path('recipes/download_shopping_cart/', DownloadShoppingList.as_view()),
    path('', include(router.urls)),
]
