from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('product/<str:store_name>/<path:product_url>/', views.product_detail, name='product_detail'),
    
    # Bookmark URLs
    path('bookmark/add/<int:product_id>/', views.add_bookmark, name='add_bookmark'),
    path('bookmark/remove/<int:product_id>/', views.remove_bookmark, name='remove_bookmark'),
    path('bookmark/toggle/<int:product_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarks/', views.bookmarks_list, name='bookmarks'),
    path('bookmark/count/', views.bookmark_count_view, name='bookmark_count'),
]
