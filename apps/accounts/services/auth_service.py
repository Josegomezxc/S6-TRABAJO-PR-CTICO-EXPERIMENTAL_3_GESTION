from django.contrib.auth import login
from django.contrib.auth.models import User


def authenticate_flexible(request, identifier, password):
    from django.contrib.auth import authenticate
    user = authenticate(request, username=identifier, password=password)
    if user is None:
        user_obj = User.objects.filter(email__iexact=identifier).first()
        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
    return user


def login_single_session(request, user):
    login(request, user)
