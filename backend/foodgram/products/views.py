import django_filters
from rest_framework import viewsets, status
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from .filters import RecipesFilter
from .serializers import RecipeListSerializer, RecipeCreateSerializer
from .models import Recipe
from .permissions import IsAdminPermission, RecipeAccessPermission


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filter_class = RecipesFilter
    permission_classes = [IsAdminPermission, RecipeAccessPermission]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer
