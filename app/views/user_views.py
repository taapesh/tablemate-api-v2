from django.shortcuts import render
from django.db import transaction, IntegrityError
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from rest_framework.authtoken.models import Token

from app.models import Table, Server, Restaurant, Order, Receipt, MenuItem
from decimal import Decimal, ROUND_HALF_UP

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_user(request):
    return Response(request.user.to_json(), status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_nearby_restaurants(request):
    restaurants = Restaurant.objects.all()
    return Response([r.to_json() for r in restaurants], status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def create_or_join_table(request):
    restaurant_id = request.data.get("restaurant_id")
    table_number = request.data.get("table_number")

    try:
        restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)
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
def pay(request):
    if request.user.table is None:
        return Response({"message": "User does not have a table"}, status=status.HTTP_404_NOT_FOUND)

    '''
    1. Get list of all active orders for user
    2. Create new receipt object for user
    3. Iterate through orders and:
        - add order price to total
        - order.active = False
        - set order receipt
    4. Decrement table size (if 0, deactivate table)
    5. Set user's table to None
    '''

    orders = list(Order.objects.filter(customer=request.user, active=True))

    Receipt.objects.all().delete()
    receipt = Receipt.objects.create(
        customer=request.user, restaurant=request.user.table.restaurant)

    total = Decimal()
    for order in orders:
        total += order.item.price
        order.active = False
        order.receipt = receipt
        order.save()
    receipt.total_bill = total
    receipt.save()

    ####################
    # TODO: Make payment
    ####################

    table = request.user.table
    table.size -= 1

    # If last member of table leaves, deactivate table
    if table.size == 0:
        table.active = False
    
    table.save()

    request.user.table = None
    request.user.save()

    return Response(receipt.to_json(), status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_user_table(request):
    if request.user.table is not None:
        return Response(request.user.table.to_json(), status=status.HTTP_200_OK)
    return Response({"message": "User does not have a table"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def make_request(request):
    table = request.user.table
    if table is None:
        return Response({"message": "User does not have a table"}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        if not table.requested:
            table.requested = True
            table.save()
            return Response({"message": "Request made"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Request already made"}, status=status.HTTP_409_CONFLICT)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def add_to_order(request):
    if request.user.table is None:
        return Response({"message": "User does not have a table"}, status=status.HTTP_404_NOT_FOUND)

    try:
        item = MenuItem.objects.get(item_id=request.data.get("item_id"))
    except MenuItem.DoesNotExist:
        return Response({"message": "Menu item does not exist"}, status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.create(item=item, customer=request.user, table=request.user.table)
    return Response(order.to_json(), status=status.HTTP_201_CREATED)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def place_order(request):
    if request.user.table is None:
        return Response({"message": "User does not have a table"}, status=status.HTTP_404_NOT_FOUND)

    Order.objects.filter(customer=request.user, pending=True).update(
        pending=False, active=True)

    return Response({}, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_user_pending_orders(request):
    orders = Order.objects.filter(customer=request.user, pending=True)
    return Response([o.to_json() for o in orders], status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_user_active_orders(request):
    orders = Order.objects.filter(customer=request.user, active=True)
    return Response([o.to_json() for o in orders], status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_user_order(request, order_id):
    try:
        order = Order.objects.get(customer=request.user, order_id=order_id)
        return Response(order.to_json(), status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({"message": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_user_receipts(request):
    receipts = Receipt.objects.filter(customer=request.user)
    return Response([r.to_json() for r in receipts], status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_user_receipt(request, receipt_id):
    try:
        receipt = Receipt.objects.get(customer=request.user, receipt_id=receipt_id)
        return Response(receipt.to_json(), status=status.HTTP_200_OK)
    except Receipt.DoesNotExist:
        return Response({"message": "Receipt does not exist"}, status=status.HTTP_404_NOT_FOUND)
