from rest_framework import serializers
from .models import Recipe, FavoriteRecipes, Tag, Ingredient, ShoppingCart, Product
from users.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField


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


class RecipeSerializer(serializers.ModelSerializer):
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

    def create_ingredient(self, ingredients):
        ingredients_ids = []
        for ingredient in ingredients:
            obj = Ingredient.objects.get_or_create(
                name=Product.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
            ingredients_ids.append(obj[0].id)
        return ingredients_ids

    def create(self, validated_data):
        tags_ids = self.context['request'].data['tags']
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            name=validated_data['name'],
            image=validated_data['image'],
            text=validated_data['text'],
            cooking_time=validated_data['cooking_time']
        )
        request_ingredients_data = self.context['request'].data['ingredients']
        ingredients_ids = self.create_ingredient(request_ingredients_data)
        recipe.ingredients.set(ingredients_ids)
        recipe.tags.set(tags_ids)
        return recipe

    def update(self, instance, validated_data):
        tags_ids = self.context['request'].data['tags']
        instance.name = validated_data['name']
        instance.image = validated_data['image']
        instance.cooking_time = validated_data['cooking_time']
        instance.text = validated_data['text']
        request_ingredients_data = self.context['request'].data['ingredients']
        ingredients_ids = self.create_ingredient(request_ingredients_data)
        instance.ingredients.set(ingredients_ids)
        instance.tags.set(tags_ids)
        return instance

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        return FavoriteRecipes.objects.filter(user=current_user,
                                              recipes=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        return ShoppingCart.objects.filter(user=current_user,
                                           cart=obj).exists()
