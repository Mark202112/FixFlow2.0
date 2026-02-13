"""Django Admin - для управління даними"""
from django.contrib import admin
from .models import Client, Employee, Order

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('created_at',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'role')
    list_filter = ('role',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'client', 'device', 'status', 'assigned_master', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'device', 'client__name')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
