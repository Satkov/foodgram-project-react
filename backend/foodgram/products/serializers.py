from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Recipe, FavoriteRecipes, Tag, Ingredient, ShoppingCart, Product
from users.models import Follow
from users.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField

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
    name = serializers.CharField(source="name.name")
    measurement_unit = serializers.CharField(source="name.measurement_unit")

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')

    def to_representation(self, value):
        data = {
            "id": value.id,
            "name": value.name.name,
            "measurement_unit": value.name.measurement_unit,
            "amount": value.amount
        }
        return data


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
        current_user = self.context['request'].user
        return FavoriteRecipes.objects.filter(user=current_user,
                                              recipes=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        return ShoppingCart.objects.filter(user=current_user,
                                           cart=obj).exists()


class MyPrimaryKeyRelatedTagField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        data = {
            "id": value.id,
            "name": value.name,
            "color": value.color,
            "slug": value.slug
        }
        return data


class RecipeCreateSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = IngredientCreateSerializer(many=True)
    author = UserSerializer(many=False, read_only=True)
    image = Base64ImageField(required=True)
    tags = MyPrimaryKeyRelatedTagField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def GetOrCreateIngredients(self, validated_data):
        ingredients_ids = []
        for i in range(len(validated_data['ingredients'])):
            ing = Ingredient.objects.get_or_create(
                name=validated_data['ingredients'][i]['id'],
                amount=validated_data['ingredients'][i]['amount']
            )
            ingredients_ids.append(ing[0].id)
        return ingredients_ids

    def create(self, validated_data):
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            name=validated_data['name'],
            image=validated_data['image'],
            text=validated_data['text'],
            cooking_time=validated_data['cooking_time']
        )
        ingredients_ids = self.GetOrCreateIngredients(validated_data)
        recipe.ingredients.set(ingredients_ids)
        recipe.tags.set(validated_data['tags'])
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.image = validated_data['image']
        instance.cooking_time = validated_data['cooking_time']
        instance.text = validated_data['text']
        ingredients_ids = self.GetOrCreateIngredients(validated_data)
        instance.ingredients.set(ingredients_ids)
        instance.tags.set(validated_data['tags'])
        return instance

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        return FavoriteRecipes.objects.filter(user=current_user,
                                              recipes=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        return ShoppingCart.objects.filter(user=current_user,
                                           cart=obj).exists()


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def create(self, validated_data):
        recipe = Recipe.objects.get(pk=validated_data['recipe_id'])
        if FavoriteRecipes.objects.filter(user=self.context['request'].user,
                                          recipes=recipe).exists():
            raise serializers.ValidationError('Вы уже подписаны на этот рецепт')
        FavoriteRecipes.objects.create(
            user=self.context['request'].user,
            recipes=recipe)
        return recipe


class SubscribeUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        if current_user == obj:
            return True
        return Follow.objects.filter(user=obj,
                                     author=current_user.id).exists()


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def validate(self, data):
        author = data['author']
        user = data['user']
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
        author = validated_data['author']
        user = validated_data['user']
        follow = Follow.objects.create(
            user=user,
            author=author
        )
        return follow

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        if current_user == obj:
            return True
        return Follow.objects.filter(user=obj,
                                     author=current_user.id).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        serializer = FavoriteRecipesSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()