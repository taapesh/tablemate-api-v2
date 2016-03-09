from rest_framework import serializers
from models import TablemateUser, Table

class TableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table

        fields = (
            "table_id",
            "size",
            "server_id",
            "server_name",
            "restaurant_name",
            "restaurant_addr",
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