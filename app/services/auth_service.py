from rest_framework.authtoken.models import Token

from app.models import TablemateUser


def register(first_name, last_name, email, password):
    user = TablemateUser.objects.create_user(
        first_name=first_name, last_name=last_name, email=email, password=password)
    user.token = get_auth_token(user)
    return user


def get_all_users():
    return TablemateUser.objects.all()


def get_auth_token(user):
    token = Token.objects.get_or_create(user=user)
    return token[0].key


def login(email, password):
    user = TablemateUser.objects.get(email=email)
    if user.check_password(password):
        user.token = get_auth_token(user)
        return user
    else:
        return None