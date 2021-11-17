from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingList, FavoriteViewSet, FollowViewSet,
                    IngredientViewSet, RecipeViewSet, ShoppingCartViewSet,
                    TagViewSet)

router = DefaultRouter()

router.register(r'recipes', RecipeViewSet)
router.register(r'recipes', ShoppingCartViewSet)
router.register(r'recipes', FavoriteViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'users', FollowViewSet)

urlpatterns = [
    path('recipes/download_shopping_cart/', DownloadShoppingList.as_view(),
         name='download_shopping_cart'),
    path('', include(router.urls)),
]
