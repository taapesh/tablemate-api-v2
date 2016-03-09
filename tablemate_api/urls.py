from django.conf.urls import url
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Authentication API
    url(r'^auth/login/?$', views.login),
    url(r'^auth/logout/?$', views.logout),
    url(r'^auth/register/?$', views.register),

    # Table API
    url(r'^tables/(?P<table_id>[^/]+)/?$', views.get_table),
    url(r'^tables/?$', views.tables),

    # User API
    url(r'^user/table/?$', views.get_user_table),
    url(r'^user/(?P<user_id>[^/]+)/?$', views.user),

    # Server API
    url(r'^server/(?P<server_id>[^/]+)/tables/?$', views.get_server_tables),
]
