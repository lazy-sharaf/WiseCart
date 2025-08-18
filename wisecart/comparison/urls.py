from django.urls import path
from . import views

app_name = 'comparison'

urlpatterns = [
    path('', views.comparison_page, name='compare'),
    path('add/', views.add_to_compare, name='add'),
    path('add-featured/', views.add_featured_to_compare, name='add_featured'),
    path('remove/', views.remove_from_compare, name='remove'),
    path('count/', views.get_compare_count, name='count'),
    path('clear/', views.clear_comparison, name='clear'),
] 