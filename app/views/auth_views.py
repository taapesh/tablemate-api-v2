from django.shortcuts import render
from django.db import transaction, IntegrityError
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from rest_framework.authtoken.models import Token

from app.models import TablemateUser

@api_view(["POST"])
def register(request):
    email = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    
    try:
        with transaction.atomic():
            user = TablemateUser.objects.create_user(first_name, last_name, email, password)
            token = Token.objects.get_or_create(user=user)
            res = user.to_json()
            res["auth_token"] = token[0].key

            return Response(res, status=status.HTTP_201_CREATED)

    except IntegrityError:
        return Response({"message": "Email already in use"}, status=status.HTTP_409_CONFLICT)

@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user = TablemateUser.objects.get(email=email)
        if user.check_password(password):
            token = Token.objects.get_or_create(user=user)

            res = user.to_json()
            res["auth_token"] = token[0].key
            return Response(res, status=status.HTTP_200_OK)

        else:
            return Response({
                "message": "Invalid credentials"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except TablemateUser.DoesNotExist:
        return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response({"message": "Logged out"}, status=status.HTTP_200_OK)

@api_view(["POST"])
def clear(request):
    from app.models import Table, Restaurant, Server, Order, Receipt, MenuCategory, MenuItem
    Restaurant.objects.all().delete()
    Table.objects.all().delete()
    Server.objects.all().delete()
    Order.objects.all().delete()
    Receipt.objects.all().delete()
    MenuCategory.objects.all().delete()
    MenuItem.objects.all().delete()
    TablemateUser.objects.all().delete()
    return Response({"message": "Cleared database"}, status=status.HTTP_200_OK)


