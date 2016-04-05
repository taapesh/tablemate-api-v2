from django.shortcuts import render
from django.core import serializers
from django.db import transaction, IntegrityError
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from rest_framework.authtoken.models import Token

from app.models import TablemateUser, Table, Server, Restaurant, MenuItem, MenuCategory

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_user_table(request):
    table = request.user.table
    if table is not None:
        return Response(table.to_json(), status=status.HTTP_200_OK)
    else:
        return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def start_serving(request):
    restaurant = Restaurant.objects.get(address=request.data.get("restaurant_addr"))
    Server.objects.filter(user=request.user, restaurant=restaurant).update(active=True)
    return Response({"message": "Now serving"}, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_server_tables(request):
    tables = Table.objects.filter(server=Server.objects.get(user=request.user))
    return Response([t.to_json() for t in tables], status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def create_table(request):
    restaurant_addr = request.data.get("restaurant_addr")
    restaurant_name = request.data.get("restaurant_name")
    table_number = request.data.get("table_number")

    try:
        restaurant = Restaurant.objects.get(name=restaurant_name, address=restaurant_addr)
    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exist"}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        table, created = Table.objects.get_or_create(restaurant=restaurant, table_number=table_number)

        if created:
            server = find_server(restaurant)
            
            if server is None:
                table.delete()
                return Response({"message": "No server available"}, status=status.HTTP_409_CONFLICT)

            else:
                table.server = server

        request.user.table = table
        request.user.save()
        table.size += 1   
        table.save()

    return Response(table.to_json(), status=status.HTTP_200_OK)

def find_server(restaurant):
    servers = list(Server.objects.filter(restaurant=restaurant, active=True))

    if not servers:
        return None

    min_load_server = None
    min_load = 10000

    for server in servers:
        load = Table.objects.filter(server=server).count()
        if load < min_load:
            min_load = load
            min_load_server = server

    return min_load_server

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def request_service(request):
    with transaction.atomic():
        table = request.user.table

        if not table.requested:
            table.requested = True
            table.save()
            return Response({"message": "Request made"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Request already made"}, status=status.HTTP_409_CONFLICT)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def create_order(request):
    name = request.data.get("name")
    price = request.data.get("price")
    category = request.data.get("category")

    try:
        item = MenuItem.objects.get(name=name, price=price, category=category)
    except MenuItem.DoesNotExist:
        return Response({"message": "Menu item does not exist"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_table_orders(request):
    name = request.data.get("name")
    price = request.data.get("price")

@api_view(["POST"])
def create_menu_category(request):
    try:
        restaurant = Restaurant.objects.get(restaurant_id=request.data.get("restaurant_id")
    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exist"})

    name = request.data.get("name")

    category, created = MenuCategory.objects.get_or_create(
        restaurant=restaurant, name=name)

    if created:
        return Response({
            "message": "Created category " + category.name}, status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "Category already exists"}, status=status.HTTP_409_CONFLICT)

@api_view(["POST"])
def create_menu_item(request):
    restaurant_name = request.data.get("restaurant_name")
    restaurant_addr = request.data.get("restaurant_addr")

    try:
        restaurant = Restaurant.objects.get(name=restaurant_name, address=restaurant_addr)
    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exist"})

    name = request.data.get("name")
    price = request.data.get("price")
    category = request.data.get("category")
    description = request.data.get("description")

    item, created = MenuItem.objects.get_or_create(
        name=name, price=price, category=category, description=description, restaurant=restaurant)

    if created:
        return Response(item.to_json(), status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "Menu item already exists"}, status=status.HTTP_409_CONFLICT)

@api_view(["GET"])
def get_menu(request):
    restaurant_name = request.GET.get("restaurant_name", "")
    restaurant_addr = request.GET.get("restaurant_addr", "")

    try:
        restaurant = Restaurant.objects.get(name=restaurant_name, address=restaurant_addr)
        items = MenuItem.objects.filter(restaurant=restaurant)
        return Response([item.to_json() for item in items], status=status.HTTP_200_OK)

    except Restaurant.DoesNotExist:
        return Response({"message": "Restaurant does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
def get_menu_item(request):
    item_id = request.GET.get("item_id", "")

    try:
        item = MenuItem.objects.get(item_id=item_id)
        return Response(item.to_json(), status=status.HTTP_200_OK)
    except MenuItem.DoesNotExist:
        return Response({"message": "Menu item does not exist"}, status=status.HTTP_404_NOT_FOUND)

