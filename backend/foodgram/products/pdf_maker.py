from io import BytesIO

from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from foodgram import settings

from .models import Ingredient, ShoppingCart


def count_amount_of_all_ingredients_in_cart(current_user):
    cart = get_object_or_404(ShoppingCart, user=current_user)
    ingredients = {}
    for ingredient_id in cart.cart.all().values_list('ingredients', flat=True):
        ing = get_object_or_404(Ingredient, id=ingredient_id)
        if ing not in ingredients:
            ingredients[ing] = 0
        ingredients[ing] += ing.amount
    return ingredients


def create_list_of_str_of_ingredients(ingredients):
    ingredients_list = []
    number = 1
    for ing in ingredients.keys():
        line = (f'{number}) {ing.product.name} — '
                f'{ingredients[ing]} {ing.product.measurement_unit}')
        ingredients_list.append(line)
        number += 1
    return ingredients_list


def create_pdf(ingredients_list):
    buffer = BytesIO()
    documentTitle = 'Список покупок'
    pdf = canvas.Canvas(buffer)
    pdfmetrics.registerFont(
        TTFont('main', settings.STATIC_ROOT + '/timesnewroman.ttf')
    )
    pdf.setFont('main', 28)
    pdf.drawCentredString(300, 800, documentTitle)
    text = pdf.beginText(40, 740)
    text.setFont('main', 24)
    for line in ingredients_list:
        text.textLine(line)
    pdf.drawText(text)
    pdf.showPage()
    pdf.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
