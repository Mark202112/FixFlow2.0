"""Django Admin — управління даними"""
from django.contrib import admin
from .models import Client, Employee, Order, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display  = ('name', 'price_display', 'price_from', 'time_estimate', 'warranty', 'is_active', 'sort_order')
    list_editable = ('price_display', 'price_from', 'is_active', 'sort_order')
    list_filter   = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    save_on_top   = True

    fieldsets = (
        ('Основна інформація', {
            'fields': ('slug', 'name', 'label', 'icon', 'is_active', 'sort_order'),
        }),
        ('💰 Ціни та умови', {
            'fields': ('price_display', 'price_from', 'time_estimate', 'warranty'),
            'description': 'Змінюйте ціни тут — вони одразу відображаться на сайті.',
        }),
        ('Зміст картки', {
            'fields': ('description', 'features'),
        }),
    )

    class Media:
        css = {'all': []}  # placeholder


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display  = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')
    list_filter   = ('created_at',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'role')
    list_filter  = ('role',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ('order_number', 'client', 'device', 'status', 'assigned_master', 'price', 'created_at')
    list_filter     = ('status', 'created_at')
    search_fields   = ('order_number', 'device', 'client__name', 'client__phone')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
