from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import Follow
from users.serializers import UserSerializer
from .models import (FavoriteRecipe, Ingredient, Product, Recipe, ShoppingCart,
                     Tag)
from .utils import get_request

User = get_user_model()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="product.name")
    measurement_unit = serializers.CharField(source="product.measurement_unit")

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = IngredientSerializer(many=True, read_only=True)
    author = UserSerializer(many=False, read_only=True)
    image = Base64ImageField(required=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        current_user = get_request(self.context).user
        if current_user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=current_user,
                                             recipes=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = get_request(self.context).user
        if current_user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=current_user,
                                           cart=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    author = UserSerializer(many=False, read_only=True)
    image = Base64ImageField(required=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def validate(self, data):
        try:
            if int(data.get('cooking_time') < 1):
                raise serializers.ValidationError({
                    'errors': 'Минимальное временя готовки - 1 минута'
                })
        except ValueError:
            raise serializers.ValidationError({
                'errors': 'Время приготовления должно быть числом'
            })

        request_data = get_request(self.context).data

        ingredients_ids = []
        for ingredient in request_data.get('ingredients'):
            ingredient_id = ingredient.get('id')
            ingredient_amount = ingredient.get('amount')
            try:
                int(ingredient_id)
            except ValueError:
                raise serializers.ValidationError({
                    'errors': 'id ингредиента должно быть числом'
                })

            try:
                if int(ingredient_amount) < 1:
                    raise serializers.ValidationError({
                        'errors': 'Количество ингредиентов должно быть > 0'
                    })
            except ValueError:
                raise serializers.ValidationError({
                    'errors': 'Количество ингредиентов должно быть числом'
                })
            ingredients_ids.append(ingredient_id)

        if len(ingredients_ids) > len(set(ingredients_ids)):
            raise serializers.ValidationError({
                'errors': 'ингредиенты рецепта не должны повторяться'
            })
        tags = request_data.get('tags')
        if not all(isinstance(x, int) for x in tags):
            raise serializers.ValidationError({
                'errors': 'id тэга должен быть числом'
            })
        if len(tags) > len(set(tags)):
            raise serializers.ValidationError({
                'errors': 'Тэги не должны повторяться'
            })

        return data

    def get_or_create_ingredients(self):
        request_data = get_request(self.context).data
        ingredients_ids = []
        for ingredient in request_data.get('ingredients'):
            product = get_object_or_404(Product, id=ingredient.get('id'))
            ing = Ingredient.objects.get_or_create(
                product=product,
                amount=ingredient.get('amount')
            )
            ingredients_ids.append(ing[0].id)
        return ingredients_ids

    def create(self, validated_data):
        request_data = get_request(self.context).data
        recipe = Recipe.objects.create(
            author=get_request(self.context).user,
            name=validated_data['name'],
            image=validated_data['image'],
            text=validated_data['text'],
            cooking_time=validated_data['cooking_time']
        )
        ingredients_ids = self.get_or_create_ingredients()
        recipe.ingredients.set(ingredients_ids)
        tags_ids = request_data.get('tags')
        recipe.tags.set(tags_ids)
        return recipe

    def update(self, instance, validated_data):
        request_data = get_request(self.context).data
        super().update(instance, validated_data)
        ingredients_ids = self.get_or_create_ingredients()
        instance.ingredients.set(ingredients_ids)
        tags_ids = request_data.get('tags')
        instance.tags.set(tags_ids)
        return instance

    def get_tags(self, obj):
        tags = obj.tags.all()
        serializer = TagSerializer(tags, many=True)
        return serializer.data

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.all()
        serializer = IngredientSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        current_user = get_request(self.context).user
        return FavoriteRecipe.objects.filter(user=current_user,
                                             recipes=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = get_request(self.context).user
        return ShoppingCart.objects.filter(user=current_user,
                                           cart=obj).exists()


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        recipe = self.context.get('recipe')
        current_user = get_request(self.context).user
        if FavoriteRecipe.objects.filter(
                user=current_user, recipes=recipe).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этот рецепт'
            )
        return data

    def create(self, validated_data):
        recipe = self.context.get('recipe')
        favor_list = get_object_or_404(
            FavoriteRecipe,
            user=get_request(self.context).user
        )
        favor_list.recipes.add(recipe)
        return recipe


class SubscribeUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = get_request(self.context).user
        if current_user == obj:
            return True
        return Follow.objects.filter(user=current_user, author=obj).exists()


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def validate(self, data):
        author = self.context.get('author')
        user = get_request(self.context).user
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError({
                'errors': 'Вы уже подписались на данного пользователя'
            })
        elif user == author:
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на самого себя'
            })
        return data

    def create(self, validated_data):
        author = self.context.get('author')
        user = get_request(self.context).user
        follow, _ = Follow.objects.get_or_create(user=user)
        follow.author.add(author)
        return author

    def get_is_subscribed(self, obj):
        current_user = get_request(self.context).user
        if current_user == obj:
            return True
        return Follow.objects.filter(user=current_user, author=obj).exists()

    def get_username(self, obj):
        return self.context.get('author').username

    def get_email(self, obj):
        return self.context.get('author').email

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        serializer = FavoriteRecipesSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class ListFollowersSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        current_user = get_request(self.context).user
        if current_user == obj:
            return True
        return Follow.objects.filter(user=current_user, author=obj).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        serializer = FavoriteRecipesSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        recipe = self.context.get('recipe')
        if ShoppingCart.objects.filter(user=get_request(self.context).user,
                                       cart=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже находится в корзине'
            })
        return data

    def create(self, validated_data):
        recipe = self.context.get('recipe')
        cart, created = ShoppingCart.objects.get_or_create(
            user=get_request(self.context).user
        )
        cart.cart.add(recipe)
        return recipe
