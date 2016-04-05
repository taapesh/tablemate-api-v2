from django.conf.urls import url
from django.contrib import admin
from app.views import auth_views, restaurant_views, user_views, server_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Authentication API
    url(r'^auth/login/?$', auth_views.login),
    url(r'^auth/logout/?$', auth_views.logout),
    url(r'^auth/register/?$', auth_views.register),
    url(r'^auth/clear/?$', auth_views.clear),

    # User API
    url(r'^user/?$', user_views.get_user),
    url(r'^user/nearby_restaurants/?$', user_views.get_nearby_restaurants),
    url(r'^user/table/?$', user_views.get_user_table),
    url(r'^user/table/create_or_join/?$', user_views.create_or_join_table),
    url(r'^user/table/request/?$', user_views.make_request),
    url(r'^user/table/add_to_order/?$', user_views.add_to_order),
    url(r'^user/table/place_order/?$', user_views.place_order),
    url(r'^user/pending_orders/?$', user_views.get_user_pending_orders),
    url(r'^user/active_orders/?$', user_views.get_user_active_orders),
    url(r'^user/orders/(?P<order_id>[-\w]+)/?$', user_views.get_user_order),
    url(r'^user/receipts/?$', user_views.get_user_receipts),
    url(r'^user/receipts/(?P<receipt_id>[-\w]+)/?$', user_views.get_user_receipt),
    url(r'^user/table/pay/?$', user_views.pay),

    # Restaurant API
    url(r'^restaurant/get/?$', restaurant_views.get_restaurant_by_name),
    url(r'^restaurant/register/?$', restaurant_views.register_restaurant),
    url(r'^restaurant/(?P<restaurant_id>[-\w]+)/?$', restaurant_views.get_restaurant),
    url(r'^restaurant/(?P<restaurant_id>[-\w]+)/create_menu_category/?$',
        restaurant_views.create_menu_category),
    url(r'^restaurant/(?P<restaurant_id>[-\w]+)/create_menu_item/?$',
        restaurant_views.create_menu_item),
    url(r'^restaurant/(?P<restaurant_id>[-\w]+)/register_server/?$', restaurant_views.register_server),
    url(r'^restaurant/(?P<restaurant_id>[-\w]+)/menu_categories/?$', restaurant_views.menu_categories),
    url(r'^restaurant/(?P<restaurant_id>[-\w]+)/menu/?$', restaurant_views.get_menu),
    url(r'^restaurant/menu/(?P<item_id>[-\w]+)/?$', restaurant_views.get_menu_item),

    # Server API
    url(r'^server/restaurants/?$', server_views.get_server_restaurants),
    url(r'^server/restaurants/(?P<restaurant_id>[-\w]+)/tables/?$', server_views.get_server_tables),
    url(r'^server/tables/(?P<table_id>[-\w]+)/?$', server_views.get_server_table),
    url(r'^server/start_serving/?$', server_views.start_serving),
    url(r'^server/tables/(?P<table_id>[-\w]+)/bump/?$', server_views.bump_request),
    url(r'^server/tables/(?P<table_id>[-\w]+)/orders/?$', server_views.get_table_orders),
]
