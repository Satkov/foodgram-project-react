from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from users.models import Follow
from .filters import IngredientFilter, RecipesFilter
from .models import FavoriteRecipe, Product, Recipe, ShoppingCart, Tag
from .pagination import LimitPaginator
from .pdf_maker import (count_amount_of_all_ingredients_in_cart,
                        create_list_of_str_of_ingredients, create_pdf)
from .permissions import RecipePermission
from .serializers import (FavoriteRecipesSerializer, FollowSerializer,
                          ListFollowersSerializer, ProductSerializer,
                          RecipeCreateSerializer, RecipeListSerializer,
                          ShoppingCartSerializer, TagSerializer)

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = RecipesFilter
    permission_classes = [RecipePermission]
    pagination_class = LimitPaginator

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer


class TagViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 GenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filter_class = IngredientFilter
    pagination_class = None


class FavoriteViewSet(GenericViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['GET', 'DELETE'], url_path='favorite')
    def favorite(self, request, pk=None):
        instance = self.get_object()
        if request.method == 'GET':
            data = {
                'id': instance.id,
                'name': instance.name,
                'image': instance.image,
                'cooking_time': instance.cooking_time
            }
            serializer = FavoriteRecipesSerializer(data=data, context={
                'recipe': instance,
                'request': request
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favor_list = get_object_or_404(FavoriteRecipe, user=request.user)
            if not FavoriteRecipe.objects.filter(user=request.user,
                                                 recipes=instance).exists():
                raise ValidationError({
                    'errors': 'Рецепта нет в списке избранного'
                })
            favor_list.recipes.remove(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = LimitPaginator

    @action(detail=False, methods=['GET'], url_path='subscriptions')
    def get_subscriptions(self, request):
        followings = get_object_or_404(Follow, user=request.user).author.all()
        page = self.paginate_queryset(followings)
        if page is not None:
            serializer = ListFollowersSerializer(page, many=True, context={
                'request': self.request
            })
            return self.get_paginated_response(serializer.data)

        serializer = ListFollowersSerializer(followings, many=True, context={
                'request': self.request
            })
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET', 'DELETE'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        if request.method == 'GET':
            author = get_object_or_404(User, id=pk)
            data = {
                'email': author.email,
                'id': author.id,
                'username': author.username,
                'first_name': author.first_name,
                'last_name': author.last_name,
            }
            serializer = FollowSerializer(data=data, context={
                'request': request,
                'author': author
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            author = get_object_or_404(User, id=pk)
            follow = get_object_or_404(Follow, user=request.user)
            if not Follow.objects.filter(user=request.user,
                                         author=author).exists():
                raise ValidationError({
                    'errors': 'Вы не подписаны на этого автора'
                })
            follow.author.remove(author)
            return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(GenericViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['GET', 'DELETE'], url_path='shopping_cart')
    def add_or_delete_recipe_from_cart(self, request, pk=None):
        instance = self.get_object()
        if request.method == 'GET':
            data = {
                'id': instance.id,
                'name': instance.name,
                'image': instance.image,
                'cooking_time': instance.cooking_time,
            }
            serializer = ShoppingCartSerializer(data=data, context={
                'request': request,
                'recipe': instance
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            cart = get_object_or_404(ShoppingCart, user=request.user)
            if not ShoppingCart.objects.filter(user=request.user,
                                               cart=instance).exists():
                raise ValidationError({
                    'errors': 'Рецепта нет в корзине'
                })
            cart.cart.remove(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingList(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = 'low_request'

    def get(self, request):
        current_user = request.user
        ingredients = count_amount_of_all_ingredients_in_cart(current_user)
        ingredients_list = create_list_of_str_of_ingredients(ingredients)
        pdf = create_pdf(ingredients_list)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment;'
            'filename="shopping_list.pdf.pdf"'
        )
        response.write(pdf)
        return response
