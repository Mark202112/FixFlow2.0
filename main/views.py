import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from orders.models import Order, Client, Service


def home(request):
    services_qs = Service.objects.filter(is_active=True)

    # Dict для шаблону: slug → Service об'єкт
    services_dict = {s.slug: s for s in services_qs}

    # JSON для JavaScript serviceInfo (замість хардкоду)
    services_json = {}
    for s in services_qs:
        services_json[s.slug] = {
            'num': str(s.sort_order).zfill(2),
            'icon': s.icon,
            'label': s.label,
            'title': s.name,
            'price': s.price_display,
            'time': s.time_estimate,
            'warranty': s.warranty,
            'desc': s.description,
            'features': s.get_features_list(),
        }

    return render(request, 'main/home.html', {
        'services_dict': services_dict,
        'services_json': json.dumps(services_json, ensure_ascii=False),
    })


@require_POST
def create_order(request):
    """Створення замовлення через форму на сайті"""
    try:
        name    = request.POST.get('name', '').strip()
        phone   = request.POST.get('phone', '').strip()
        device  = request.POST.get('device', '').strip()
        problem = request.POST.get('problem', '').strip()

        if not (name and phone and device and problem):
            return JsonResponse({'success': False, 'error': 'Заповніть всі поля'}, status=400)

        client, _ = Client.objects.get_or_create(
            phone=phone,
            defaults={'name': name}
        )

        order = Order.objects.create(
            client=client,
            device=device,
            problem=problem
        )

        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'message': 'Заявку успішно створено'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
def check_status_api(request):
    """API endpoint для перевірки статусу (без перезавантаження)"""
    try:
        from orders.models import Comment

        search = request.POST.get('search', '').strip()

        if not search:
            return JsonResponse({'orders': []})

        orders = (
            Order.objects.filter(order_number__icontains=search) |
            Order.objects.filter(client__phone__icontains=search)
        ).select_related('client').prefetch_related('comments__author')[:10]

        results = []
        for order in orders:
            comments_data = [
                {
                    'text': c.text,
                    'author': c.author.name if c.author else 'Майстер',
                    'date': c.created_at.strftime('%d.%m.%Y %H:%M'),
                }
                for c in order.comments.all()
            ]

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


def check_status(request):
    return render(request, 'main/home.html')
