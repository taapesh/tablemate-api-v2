from django.conf.urls import url
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Authentication API
    url(r'^auth/login/?$', views.login),
    url(r'^auth/logout/?$', views.logout),
    url(r'^auth/register/?$', views.register),
    url(r'^auth/register_server/?$', views.register_server),

    # Table API
    url(r'^table/request_service/?$', views.request_service),
    url(r'^tables/?$', views.tables),

    # User API
    url(r'^user/table/?$', views.get_user_table),

    # Server API
    url(r'^server/tables/?$', views.get_server_tables),
]
