from django.shortcuts import render
from django.db import transaction, IntegrityError
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from rest_framework.authtoken.models import Token

from app.models import TablemateUser, Restaurant, Server, MenuItem, MenuCategory

@api_view(["POST"])
def register_restaurant(request):
    restaurant, created = Restaurant.objects.get_or_create(
        name=request.data.get("name"),
        address=request.data.get("address")
    )

    if created:
        return Response(restaurant.to_json(), status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "Restaurant already exists"}, status=status.HTTP_409_CONFLICT)

@api_view(["GET"])
def get_restaurant_by_name(request):
    try:
        restaurant = Restaurant.objects.get(
            name=request.data.get('name'),
            address=request.data.get('address'))
        return Response(restaurant.to_json(), status=status.HTTP_200_OK)
    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exist"}, status=status.HTTP_404_NOT_FOUND)
@api_view(["GET"])
def get_restaurant(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
        return Response(restaurant.to_json(), status=status.HTTP_200_OK)
    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["POST"])
def register_server(request, restaurant_id):
    email = request.data.get("email")
    
    try:
        user = TablemateUser.objects.get(email=email)
    except TablemateUser.DoesNotExist:
        return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

    try:
        restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exist"}, status=status.HTTP_404_NOT_FOUND)

    server, created = Server.objects.get_or_create(
        restaurant=restaurant,
        user=user
    )

    if created:
        return Response(server.to_json(), status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "Server already exists"}, status=status.HTTP_409_CONFLICT)
    
@api_view(["POST"])
def create_menu_category(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exist"})

    name = request.data.get("name")
    if name is None:
        return Response({
            "message": "Must provide a category name"}, status=status.HTTP_400_BAD_REQUEST)

    category, created = MenuCategory.objects.get_or_create(
        restaurant=restaurant, name=name)

    if created:
        return Response({
            "message": "Created category: " + category.name}, status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "Category already exists"}, status=status.HTTP_409_CONFLICT)

@api_view(["POST"])
def create_menu_item(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exist"}, status=status.HTTP_404_NOT_FOUND)

    try:
        category_name = request.data.get("category")
        category = MenuCategory.objects.get(name=category_name, restaurant=restaurant)
    except MenuCategory.DoesNotExist:
        return Response({"message": "Category does not exist"}, status=status.HTTP_404_NOT_FOUND)

    name = request.data.get("name")
    price = request.data.get("price")
    description = request.data.get("description")

    item, created = MenuItem.objects.get_or_create(
        name=name, price=price, category=category, description=description, restaurant=restaurant)

    if created:
        return Response(item.to_json(), status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "Menu item already exists"}, status=status.HTTP_409_CONFLICT)

@api_view(["GET"])
def get_menu(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
        items = MenuItem.objects.filter(restaurant=restaurant)
        return Response([item.to_json() for item in items], status=status.HTTP_200_OK)

    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
def menu_categories(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
        categories = MenuCategory.objects.filter(restaurant=restaurant)
        return Response([category.to_json() for category in categories], status=status.HTTP_200_OK)
    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
def get_menu_item(request, item_id): 
    try:
        item = MenuItem.objects.get(item_id=item_id)
        return Response(item.to_json(), status=status.HTTP_200_OK)
    except MenuItem.DoesNotExist:
        return Response({"message": "Menu item does not exist"}, status=status.HTTP_404_NOT_FOUND)

