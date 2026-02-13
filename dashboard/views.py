from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from orders.models import Order, Client, Employee

@login_required
def dashboard_home(request):
    """Головна сторінка зі статистикою"""
    # Перевірка наявності профілю співробітника для безпеки
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        employee = None # Щоб не "лягла" сторінка, якщо зайшов суперюзер без профілю

    orders = Order.objects.all()
    
    context = {
        'employee': employee,
        'total_orders': orders.count(),
        'new_orders': orders.filter(status='new').count(),
        'in_progress': orders.filter(status='in_progress').count(),
        'total_revenue': orders.filter(status='completed').aggregate(Sum('price'))['price__sum'] or 0,
        
        # Використовуємо саме 'orders' для карток (Крок 3), а не 'recent_orders'
        'orders': orders[:6], 
        
        'stats_labels': ['Нові', 'В роботі', 'Готові', 'Видані'],
        'stats_data': [
            orders.filter(status='new').count(),
            orders.filter(status='in_progress').count(),
            orders.filter(status='ready').count(),
            orders.filter(status='completed').count(),
        ]
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def orders_list(request):
    """Список усіх замовлень з покращеною фільтрацією"""
    query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    orders = Order.objects.all()
    
    if query:
        # Шукаємо по номеру замовлення, пристрою АБО імені клієнта
        orders = orders.filter(
            Q(order_number__icontains=query) | 
            Q(device__icontains=query) | 
            Q(client__name__icontains=query)
        )
    if status_filter:
        orders = orders.filter(status=status_filter)
        
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
        'search_query': query,
    }
    return render(request, 'dashboard/orders_list.html', context)

@login_required
def order_detail(request, order_number):
    """Деталі замовлення"""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'dashboard/order_detail.html', {'order': order})

@login_required
def clients_list(request):
    """Список клієнтів з пошуком"""
    query = request.GET.get('search', '')
    clients = Client.objects.all()
    
    if query:
        clients = clients.filter(Q(name__icontains=query) | Q(phone__icontains=query))
        
    return render(request, 'dashboard/clients_list.html', {
        'clients': clients,
        'search_query': query
    })

# --- Тимчасові заглушки для авторизації ---
def login_view(request): 
    # Тут краще зробити справжню авторизацію пізніше
    return render(request, 'dashboard/login.html')

def logout_view(request): 
    from django.contrib.auth import logout
    logout(request)
    return redirect('dashboard:login')

def create_client(request):
    # Потрібно буде зробити форму (ModelForm)
    return render(request, 'dashboard/client_form.html')

def calendar_view(request): return render(request, 'dashboard/calendar.html')
def reports_view(request): return render(request, 'dashboard/reports.html')