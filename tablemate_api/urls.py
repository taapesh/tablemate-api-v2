from django.conf.urls import url
from django.contrib import admin
from app.views import auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Authentication API
    url(r'^auth/register/?$', auth_views.register),
    url(r'^auth/login/?$', auth_views.login),
]
