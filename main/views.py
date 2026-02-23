from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from orders.models import Order, Client

def home(request):
    return render(request, 'main/home.html')

@require_POST
def create_order(request):
    """Створення замовлення через форму на сайті"""
    try:
        name    = request.POST.get('name', '').strip()
        phone   = request.POST.get('phone', '').strip()
        email   = request.POST.get('email', '').strip()
        device  = request.POST.get('device', '').strip()
        problem = request.POST.get('problem', '').strip()
        
        if not (name and phone and device and problem):
            return JsonResponse({'success': False, 'error': 'Заповніть всі поля'}, status=400)
        
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
        
        # Повертаємо успішну відповідь
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'message': 'Заявку успішно створено'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def check_status(request):
    """Перевірка статусу замовлення"""
    orders = None
    
    if request.method == 'POST':
        search = request.POST.get('search', '').strip()
        if search:
            # Шукаємо по номеру замовлення або телефону
            orders = Order.objects.filter(
                order_number__icontains=search
            ) | Order.objects.filter(
                client__phone__icontains=search
            )
    
    return render(request, 'main/home.html', {'orders': orders})

@require_POST
def check_status_api(request):
    """API endpoint для перевірки статусу (без перезавантаження сторінки)"""
    try:
        from orders.models import Comment
        
        search = request.POST.get('search', '').strip()
        
        if not search:
            return JsonResponse({'orders': []})
        
        # Шукаємо по номеру замовлення або телефону
        orders = Order.objects.filter(
            order_number__icontains=search
        ) | Order.objects.filter(
            client__phone__icontains=search
        )
        
        orders = orders.select_related('client').prefetch_related('comments__author')[:10]
        
        # Серіалізуємо в JSON
        results = []
        for order in orders:
            # Коментарі для клієнта
            comments_data = []
            for comment in order.comments.all():
                comments_data.append({
                    'text': comment.text,
                    'author': comment.author.name if comment.author else 'Майстер',
                    'date': comment.created_at.strftime('%d.%m.%Y %H:%M'),
                })
            
            results.append({
                'order_number': order.order_number,
                'device': order.device,
                'phone': order.client.phone,
                'status': order.status,
                'status_display': order.get_status_display(),
                'comments': comments_data,
                'created': order.created_at.strftime('%d.%m.%Y'),
            })
        
        return JsonResponse({'orders': results})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
