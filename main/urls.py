from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_order, name='create_order'),
    path('success/', views.order_success, name='order_success'),
    path('check/', views.check_status, name='check_status'),
]
