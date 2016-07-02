from django.db import IntegrityError
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from app.services import place_service


@api_view(["GET", "POST"])
def places_list(request):
    if request.method == "GET":
        places = place_service.get_all()
        return Response([p.to_json() for p in places], status=status.HTTP_200_OK)
    elif request.method == "POST":
        name = request.data.get("name")
        address = request.data.get("address")

        try:
            place = place_service.create(name, address)
            return Response(place.to_json(), status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"message": "That address is already registered"}, status=status.HTTP_409_CONFLICT)
