from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    path('shop/<slug:shop_slug>/', views.shop_detail, name='shop_detail'),
    path('', views.shops, name='shops'),
    path('featured/', views.featured_shops, name='featured_shops'),
]
