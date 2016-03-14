from django.shortcuts import render
from django.db import transaction, IntegrityError
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from rest_framework.authtoken.models import Token

from app.models import TablemateUser, Table, ServerRegistration
from app.serializers import UserSerializer, TableSerializer, RegistrationSerializer

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

            return Response({
                "auth_token": token[0].key,
                "user_id": user.user_id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }, status=status.HTTP_201_CREATED)

    except IntegrityError:
        return Response({"message": "Email already in use"}, status=status.HTTP_409_CONFLICT)

@api_view(["POST"])
def register_server(request):
    server_id = request.data.get("server_id")
    restaurant_name = request.data.get("restaurant_name")
    restaurant_addr = request.data.get("restaurant_addr")

    registration, created = ServerRegistration.objects.get_or_create(
        server_id=server_id,
        restaurant_name=restaurant_name,
        restaurant_addr=restaurant_addr
    )

    if created:
        serializer = RegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    else:
        return Response({"message": "Registration already exists"}, status=status.HTTP_409_CONFLICT)


@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user = TablemateUser.objects.get(email=email)
        if user.check_password(password):
            token = Token.objects.get_or_create(user=user)

            return Response(
            {
                "auth_token": token[0].key,
                "user_id": user.user_id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "active_table_id": user.active_table_id
            },
            status=status.HTTP_200_OK)

        else:
            return Response({
                "message": "Invalid credentials"
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    except TablemateUser.DoesNotExist:
        return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
def clear_tests(request):
    TablemateUser.objects.all().delete()
    ServerRegistration.objects.all().delete()
    Table.objects.all().delete()
    return Response({"message": "Deleted"}, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response({"message": "Logged out"}, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_user_table(request):
    try:
        table = Table.objects.get(table_id=request.user.active_table_id)
        serializer = TableSerializer(table)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Table.DoesNotExist:
        return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def start_serving(request):
    ServerRegistration.objects.filter(server_id=request.user.user_id).update(active=True)
    return Response({"message": "Now serving"}, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_server_tables(request):
    tables = Table.objects.filter(server_id=request.user.user_id)
    serializer = TableSerializer(tables, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def create_table(request):
    restaurant_addr = request.data.get("restaurant_addr")
    restaurant_name = request.data.get("restaurant_name")
    table_number = request.data.get("table_number")

    with transaction.atomic():
        table, created = Table.objects.get_or_create(
            restaurant_name=restaurant_name,
            restaurant_addr=restaurant_addr,
            table_number=table_number
        )

        if created:
            server_id = find_server(restaurant_addr)
            
            if server_id == -1:
                table.delete()
                return Response({"message": "No server available"}, status=status.HTTP_409_CONFLICT)

            else:
                server_name = TablemateUser.objects.get(user_id=server_id)
                table.server_id = server_id
                table.server_name = server_name
                table.size += 1
                request.user.active_table_id = table.table_id
                request.user.save()
                table.save()

        else:
            table.size += 1   
            table.save()

    serializer = TableSerializer(table)
    return Response(serializer.data, status=status.HTTP_200_OK)

def find_server(restaurant_addr):
    servers = list(ServerRegistration.objects.filter(
        restaurant_addr=restaurant_addr,
        active=True
    ))

    if not servers:
        return -1

    min_load_server_id = -1
    min_load = 10000

    for server in servers:
        load = Table.objects.filter(server_id=server.server_id).count()
        if load < min_load:
            min_load = load
            min_load_server_id = server.server_id

    return min_load_server_id

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def request_service(request):
    try:
        with transaction.atomic():
            table = Table.objects.get(table_id=request.user.active_table_id)

            if not table.requested:
                table.requested = True
                table.save()
                return Response({"message": "Request made"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Request already made"}, status=status.HTTP_409_CONFLICT)

    except Table.DoesNotExist:
        return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)
