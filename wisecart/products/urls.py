from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('product/<str:store_name>/<path:product_url>/', views.product_detail, name='product_detail'),
]
