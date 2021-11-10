import django_filters
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .filters import RecipesFilter
from .serializers import RecipeListSerializer, RecipeCreateSerializer, TagSerializer, ProductSerializer, \
    FavoriteRecipesSerializer, FollowSerializer
from .models import Recipe, Tag, FavoriteRecipes, Product
from .permissions import IsAdminPermission, RecipeAccessPermission
from users.models import Follow

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filter_class = RecipesFilter
    permission_classes = [IsAdminPermission, RecipeAccessPermission]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer


class TagViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 GenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [IsAdminPermission, RecipeAccessPermission]


class IngredientViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAdminPermission, RecipeAccessPermission]


class FavoriteApiView(APIView):
    serializer_class = FavoriteRecipesSerializer
    queryset = Recipe.objects.all()

    # permission_classes = [IsAdminPermission, RecipeAccessPermission]

    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        data = {
            "id": recipe.id,
            "name": recipe.name,
            "image": recipe.image,
            "cooking_time": recipe.cooking_time
        }
        serializer = FavoriteRecipesSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(recipe_id=recipe_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = Recipe.objects.get(pk=recipe_id)
        favor = FavoriteRecipes.objects.get(user=request.user,
                                            recipes=recipe)
        favor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        follows = Follow.objects.filter(user=self.request.user)
        following = []
        for follow in follows:
            following.append(follow.author)
        return following

    @action(detail=True, methods=['DELETE'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        if request.method == 'GET':
            author = get_object_or_404(User, id=pk)
            serializer = self.get_serializer(author)
            data = {
                'author': author,
                'user': request.user
            }
            validated_data = serializer.validate(data)
            serializer.create(validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            author = get_object_or_404(User, id=pk)
            Follow.objects.get(user=request.user,
                               author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
