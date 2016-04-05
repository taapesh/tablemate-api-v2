from rest_framework import serializers
from models import TablemateUser, Table, Server

class TableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table

        fields = (
            "table_id",
            "server",
            "restaurant",
            "size",
            "table_number",
            "requested",
            "time_start",
            "time_end",
        )

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = TablemateUser

        fields = (
            "user_id",
            "email",
            "first_name",
            "last_name",
            "active_table_id",
        )

class ServerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Server

        fields = (
            "server_id",
            "restaurant_name",
            "restaurant_addr",
            "active",
        )