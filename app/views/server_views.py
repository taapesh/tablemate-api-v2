from django.shortcuts import render
from django.db import transaction, IntegrityError
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from rest_framework.authtoken.models import Token

from app.models import Table, Server, Restaurant, Order

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_server_restaurants(request):
    servers = Server.objects.filter(user=request.user)
    return Response([s.restaurant.to_json() for s in servers])

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_server_tables(request, restaurant_id):
    server = get_server(request.user, restaurant_id)
    if server is None:
        return Response({"message": "Server does not exist"}, status=status.HTTP_404_NOT_FOUND)

    tables = Table.objects.filter(server=server, active=True)
    return Response([t.to_json() for t in tables], status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_server_table(request, table_id):
    try:
        table = Table.objects.get(table_id=table_id)
        return Response(table.to_json(), status=status.HTTP_200_OK)
    except Table.DoesNotExist:
        return Response({"message": "Table does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def start_serving(request):
    server = get_server(request.user, request.data.get("restaurant_id"))
    if server is None:
        return Response({"message": "Server does not exist"}, status=status.HTTP_404_NOT_FOUND)

    server.active = True
    server.save()
    return Response({"message": "Now serving"}, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def bump_request(request, table_id):
    try:
        table = Table.objects.get(table_id=table_id)
        table.requested = False
        table.save()
        return Response({"message": "Request bumped"}, status=status.HTTP_200_OK)
    except Table.DoesNotExist:
        return Response({"message": "Table does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_table_orders(request, table_id):
    try:
        table = Table.objects.get(table_id=table_id)
        orders = Order.objects.filter(table=table)
        return Response([o.to_json() for o in orders], status=status.HTTP_200_OK)
    except Table.DoesNotExist:
        return Response({"message": "Table does not exist"}, status=status.HTTP_404_NOT_FOUND)

def get_server(user, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
    except Restaurant.DoesNotExist:
        return None

    try:
        return Server.objects.get(user=user, restaurant=restaurant)
    except Server.DoesNotExist:
        return None
