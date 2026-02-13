"""Публічні сторінки - ПРОСТІ ФУНКЦІЇ"""
from django.shortcuts import render, redirect
from orders.models import Client, Order

def home(request):
    """Головна сторінка"""
    return render(request, 'main/home.html')

def create_order(request):
    """Створення замовлення"""
    if request.method == 'POST':
        # Отримуємо дані
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email', '')
        device = request.POST.get('device')
        problem = request.POST.get('problem')
        
        # Створюємо або знаходимо клієнта
        client, _ = Client.objects.get_or_create(
            phone=phone,
            defaults={'name': name, 'email': email}
        )
        
        # Створюємо замовлення
        order = Order.objects.create(
            client=client,
            device=device,
            problem=problem
        )
        
        # Зберігаємо в сесії
        request.session['last_order'] = order.order_number
        return redirect('order_success')
    
    return render(request, 'main/create_order.html')

def order_success(request):
    """Успіх"""
    number = request.session.get('last_order')
    order = Order.objects.filter(order_number=number).first() if number else None
    return render(request, 'main/order_success.html', {'order': order})

def check_status(request):
    """Перевірка статусу"""
    orders = []
    if request.method == 'POST':
        search = request.POST.get('search')
        orders = Order.objects.filter(order_number__icontains=search) | \
                 Order.objects.filter(client__phone__icontains=search)
    return render(request, 'main/check_status.html', {'orders': orders})
