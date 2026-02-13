from django.urls import path
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard_home, name='home'),
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('clients/', views.clients_list, name='clients_list'),
    path('clients/create/', views.create_client, name='create_client'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('reports/', views.reports_view, name='reports'),
]
