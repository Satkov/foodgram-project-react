from io import BytesIO

import django_filters
from django.contrib.auth import get_user_model
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from .filters import RecipesFilter
from .serializers import RecipeListSerializer, RecipeCreateSerializer, TagSerializer, ProductSerializer, \
    FavoriteRecipesSerializer, FollowSerializer, ShoppingCartSerializer
from .models import Recipe, Tag, FavoriteRecipes, Product, ShoppingCart
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

    @action(detail=True, methods=['GET', 'DELETE'], url_path='subscribe')
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


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    queryset = Recipe.objects.all()

    @action(detail=True, methods=['GET', 'DELETE'], url_path='shopping_cart')
    def add_or_delete_recipe_from_cart(self, request, pk=None):
        instance = self.get_object()
        if request.method == 'GET':
            serializer = self.get_serializer(instance)
            data = {
                'id': instance.id
            }
            validated_data = serializer.validate(data)
            serializer.create(validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            cart = get_object_or_404(ShoppingCart, user=request.user)
            if instance not in cart.cart.all():
                raise ValidationError({
                    'errors': 'Рецепта нет в корзине'
                })
            cart.cart.remove(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingList(APIView):
    def get(self, request):
        current_user = request.user
        cart = ShoppingCart.objects.get(user=current_user)
        # Считаем общую граммовку продуктов из всех рецептов
        ingredients = {}
        for recipe in cart.cart.all():
            for ing in recipe.ingredients.all():
                if ing.name not in ingredients:
                    ingredients[ing.name] = 0
                ingredients[ing.name] += ing.amount
        # Создаем список ингридиентов, который передадим в PDF
        cart_list = []
        number = 1
        for ing in ingredients:
            line = f'{number}) {ing.name} — {ingredients[ing]} {ing.measurement_unit}'
            cart_list.append(line)
            number += 1
        # Создаем PDF файл
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment;'
            ' filename="shopping_list.pdf.pdf"'
        )

        buffer = BytesIO()
        documentTitle = 'Список покупок'
        pdf = canvas.Canvas(buffer)
        pdfmetrics.registerFont(
            TTFont('main', 'times.ttf')
        )
        pdf.setFont('main', 28)
        pdf.drawCentredString(300, 800, documentTitle)
        text = pdf.beginText(40, 740)
        text.setFont('main', 14)
        for line in cart_list:
            text.textLine(line)

        pdf.drawText(text)
        pdf.showPage()
        pdf.save()
        p = buffer.getvalue()
        buffer.close()
        response.write(p)
        return response
