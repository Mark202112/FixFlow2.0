from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta, datetime
import json
from orders.models import Order, Client, Employee

def get_employee(request):
    try:
        return request.user.employee
    except Exception:
        return None

def check_deadlines_and_notify():
    """Автоматична перевірка дедлайнів і створення повідомлень"""
    try:
        from orders.models import Notification
        
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Дедлайн сьогодні або завтра
        upcoming = Order.objects.filter(
            deadline__in=[today, tomorrow],
            status__in=['new', 'in_progress']
        ).select_related('assigned_master')
        
        for order in upcoming:
            if not order.assigned_master:
                continue
            
            # Перевірити чи вже є повідомлення сьогодні
            exists = Notification.objects.filter(
                employee=order.assigned_master,
                order=order,
                created_at__date=today
            ).exists()
            
            if not exists:
                days_left = (order.deadline - today).days
                if days_left == 0:
                    msg = f"⚠️ СЬОГОДНІ дедлайн: {order.order_number} ({order.device})"
                else:
                    msg = f"📅 ЗАВТРА дедлайн: {order.order_number} ({order.device})"
                
                Notification.objects.create(
                    employee=order.assigned_master,
                    order=order,
                    message=msg
                )
        
        # Прострочені дедлайни (кожні 3 дні)
        overdue = Order.objects.filter(
            deadline__lt=today,
            status__in=['new', 'in_progress']
        ).select_related('assigned_master')
        
        for order in overdue:
            if not order.assigned_master:
                continue
            
            days_overdue = (today - order.deadline).days
            
            if days_overdue % 3 == 0:
                exists = Notification.objects.filter(
                    employee=order.assigned_master,
                    order=order,
                    created_at__date=today
                ).exists()
                
                if not exists:
                    msg = f"🔴 ПРОСТРОЧЕНО {days_overdue} днів: {order.order_number}"
                    
                    Notification.objects.create(
                        employee=order.assigned_master,
                        order=order,
                        message=msg
                    )
    except:
        pass

@login_required
def dashboard_home(request):
    # Перевірка дедлайнів
    check_deadlines_and_notify()
    
    orders = Order.objects.select_related('client','assigned_master')
    
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)

    masters = Employee.objects.filter(role='master').annotate(
        active=Count('order', filter=Q(order__status='in_progress'))
    )

    chart_labels, chart_data = [], []

    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        start = timezone.make_aware(datetime.combine(d, datetime.min.time()))
        end = timezone.make_aware(datetime.combine(d, datetime.max.time()))
        chart_labels.append(d.strftime('%d.%m'))
        chart_data.append(orders.filter(created_at__range=(start, end)).count())
    
    # Отримати повідомлення
    try:
        from orders.models import Notification
        emp = get_employee(request)
        notifications = []
        unread_count = 0
        
        if emp:
            notifications = Notification.objects.filter(
                employee=emp,
                is_read=False
            ).order_by('-created_at')[:5]
            unread_count = notifications.count()
    except:
        notifications = []
        unread_count = 0

    context = {
        'employee':    get_employee(request),
        'total':       orders.count(),
        'new_orders':  orders.filter(status='new').count(),
        'in_progress': orders.filter(status='in_progress').count(),
        'ready':       orders.filter(status='ready').count(),
        'revenue':     orders.filter(status='completed').aggregate(s=Sum('price'))['s'] or 0,
        'week_orders': orders.filter(created_at__gte=week_ago).count(),
        'recent':      orders.order_by('-created_at')[:8],
        'masters':     masters,
        'chart_labels': json.dumps(chart_labels),
        'chart_data':   json.dumps(chart_data),
        'status_choices': Order.STATUS_CHOICES,
        'notifications': notifications,
        'unread_notifications': unread_count,
    }

    return render(request, 'dashboard/home.html', context)

@login_required
def orders_list(request):
    query=request.GET.get('search','').strip()
    status_filter=request.GET.get('status','')
    master_filter=request.GET.get('master','')
    date_from=request.GET.get('date_from','')
    date_to=request.GET.get('date_to','')
    orders=Order.objects.select_related('client','assigned_master').order_by('-created_at')
    if query:
        orders=orders.filter(Q(order_number__icontains=query)|Q(device__icontains=query)|Q(client__name__icontains=query)|Q(client__phone__icontains=query))
    if status_filter: orders=orders.filter(status=status_filter)
    if master_filter: orders=orders.filter(assigned_master_id=master_filter)
    if date_from: orders=orders.filter(created_at__date__gte=date_from)
    if date_to:   orders=orders.filter(created_at__date__lte=date_to)
    all_orders=Order.objects.all()
    context={
        'orders':orders,'status_choices':Order.STATUS_CHOICES,
        'current_status':status_filter,'search_query':query,
        'masters':Employee.objects.filter(role='master'),
        'master_filter':master_filter,'date_from':date_from,'date_to':date_to,
        'counts':{'all':all_orders.count(),'new':all_orders.filter(status='new').count(),
                  'in_progress':all_orders.filter(status='in_progress').count(),'ready':all_orders.filter(status='ready').count()},
    }
    return render(request,'dashboard/orders_list.html',context)

@login_required
def order_detail(request, order_number):
    from orders.models import Comment
    
    order = get_object_or_404(Order, order_number=order_number)
    masters = Employee.objects.filter(role='master')
    comments = order.comments.all().select_related('author')

    if request.method == 'POST':
        action = request.POST.get('action', 'update')

        if action == 'update':
            status = request.POST.get('status')
            price  = request.POST.get('price', '').strip()
            master = request.POST.get('master', '')
            deadline_str = request.POST.get('deadline', '').strip()

            if status:
                order.status = status
            if price:
                try:
                    order.price = float(price)
                except ValueError:
                    pass
            if master:
                try:
                    order.assigned_master_id = int(master)
                except (ValueError, TypeError):
                    pass
            elif 'master' in request.POST and master == '':
                order.assigned_master = None
            
            # Обробка дедлайну
            if deadline_str:
                try:
                    order.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
                except:
                    pass
            elif 'deadline' in request.POST and deadline_str == '':
                order.deadline = None
            
            order.save()

        elif action == 'add_comment':
            comment_text = request.POST.get('comment', '').strip()
            if comment_text:
                Comment.objects.create(
                    order=order,
                    author=get_employee(request),
                    text=comment_text
                )

        elif action == 'delete_comment':
            comment_id = request.POST.get('comment_id')
            if comment_id:
                try:
                    comment = Comment.objects.get(pk=comment_id, order=order)
                    comment.delete()
                except Comment.DoesNotExist:
                    pass

        return redirect('dashboard:order_detail', order_number=order.order_number)

    return render(request, 'dashboard/order_detail.html', {
        'order':    order,
        'masters':  masters,
        'comments': comments,
        'today':    timezone.now().date(),
    })

@login_required
def order_delete(request, order_number):
    if request.method == 'POST':
        order = get_object_or_404(Order, order_number=order_number)
        order.delete()
    return redirect('dashboard:orders_list')

@login_required
def order_create(request):
    masters=Employee.objects.filter(role='master')
    error=None
    if request.method=='POST':
        name=request.POST.get('name','').strip()
        phone=request.POST.get('phone','').strip()
        device=request.POST.get('device','').strip()
        problem=request.POST.get('problem','').strip()
        master=request.POST.get('master','')
        price=request.POST.get('price','').strip()
        if name and phone and device and problem:
            client,_=Client.objects.get_or_create(phone=phone,defaults={'name':name})
            order=Order(client=client,device=device,problem=problem)
            if master:
                try: order.assigned_master_id=int(master); order.status='in_progress'
                except: pass
            if price:
                try: order.price=float(price)
                except: pass
            order.save()
            return redirect('dashboard:order_detail',order_number=order.order_number)
        else: error="Заповніть усі обов'язкові поля"
    return render(request,'dashboard/order_create.html',{'masters':masters,'error':error})

@login_required
def clients_list(request):
    query=request.GET.get('search','').strip()
    clients=Client.objects.annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__price',filter=Q(orders__status='completed'))
    ).order_by('-created_at')
    if query: clients=clients.filter(Q(name__icontains=query)|Q(phone__icontains=query))
    return render(request,'dashboard/clients_list.html',{'clients':clients,'search_query':query,'total':Client.objects.count()})

@login_required
def client_detail(request, pk):
    client=get_object_or_404(Client,pk=pk)
    orders=Order.objects.filter(client=client).order_by('-created_at')
    if request.method=='POST':
        client.name=request.POST.get('name',client.name).strip()
        client.save()
        return redirect('dashboard:client_detail',pk=pk)
    return render(request,'dashboard/client_detail.html',{'client':client,'orders':orders,'status_choices':Order.STATUS_CHOICES})

@login_required
def create_client(request):
    error=None
    if request.method=='POST':
        name=request.POST.get('name','').strip()
        phone=request.POST.get('phone','').strip()
        if name and phone:
            if Client.objects.filter(phone=phone).exists(): error='Клієнт з таким номером вже існує'
            else:
                c=Client.objects.create(name=name,phone=phone)
                return redirect('dashboard:client_detail',pk=c.pk)
        else: error="Ім'я та телефон обов'язкові"
    return render(request,'dashboard/create_client.html',{'error':error})

@login_required
def calendar_view(request):
    """Календар з дедлайнами - червоний і зелений"""
    from django.db.models import Q
    
    today = timezone.now().date()
    
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = today.replace(month=today.month+1, day=1) - timedelta(days=1)
    
    # Заявки з дедлайном в цьому місяці
    # НЕ видані і НЕ скасовані (вони автоматично втрачають дедлайн)
    orders = Order.objects.filter(
        deadline__gte=month_start,
        deadline__lte=month_end,
        deadline__isnull=False
    ).exclude(
        status__in=['completed', 'cancelled']
    ).select_related('client', 'assigned_master')
    
    events = []
    for o in orders:
        event = {
            'id': o.order_number,
            'title': f'{o.device[:20]}',
            'date': o.deadline.strftime('%Y-%m-%d'),
            'time': '—',
            'color': '#34c759' if o.status == 'ready' else '#ff3b30',
            'status': o.get_status_display(),
            'status_code': o.status,
            'has_deadline': True,
            'deadline': o.deadline.strftime('%d.%m.%Y'),
            'is_overdue': o.deadline < today
        }
        events.append(event)
    
    context = {
        'events_json': json.dumps(events),
        'today': today.strftime('%Y-%m-%d'),
        'month_orders': len(events)
    }
    
    return render(request, 'dashboard/calendar.html', context)

@login_required
def reports_view(request):
    period = request.GET.get('period', '30')
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')
    
    today = timezone.now().date()
    
    if date_from_str and date_to_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            period = 'custom'
            days = (date_to - date_from).days + 1
        except:
            days = 30
            date_from = today - timedelta(days=29)
            date_to = today
            period = '30'
    else:
        try:
            days = int(period)
        except:
            days = 30
        date_from = today - timedelta(days=days-1)
        date_to = today
    
    start_dt = timezone.make_aware(datetime.combine(date_from, datetime.min.time()))
    end_dt = timezone.make_aware(datetime.combine(date_to, datetime.max.time()))
    
    orders = Order.objects.filter(
        created_at__range=(start_dt, end_dt)
    ).select_related('client', 'assigned_master')
    
    total_orders_count = orders.count()

    by_status = {}
    for val, label in Order.STATUS_CHOICES:
        count = orders.filter(status=val).count()
        if count > 0:
            by_status[label] = count

    by_master = Employee.objects.filter(role='master').annotate(
        done=Count('order', filter=Q(
            order__status__in=['ready', 'completed'],
            order__created_at__range=(start_dt, end_dt)
        )),
        revenue=Sum('order__price', filter=Q(
            order__status='completed',
            order__created_at__range=(start_dt, end_dt)
        ))
    ).filter(done__gt=0)

    revenue_labels, revenue_data, orders_count_data = [], [], []

    current_date = date_from
    while current_date <= date_to:
        day_start = timezone.make_aware(datetime.combine(current_date, datetime.min.time()))
        day_end = timezone.make_aware(datetime.combine(current_date, datetime.max.time()))

        day_orders = orders.filter(created_at__range=(day_start, day_end))
        rev = day_orders.filter(status='completed').aggregate(s=Sum('price'))['s'] or 0

        revenue_labels.append(current_date.strftime('%d.%m'))
        revenue_data.append(float(rev))
        orders_count_data.append(day_orders.count())

        current_date += timedelta(days=1)

    completed_orders = orders.filter(status='completed')
    total_revenue = completed_orders.aggregate(s=Sum('price'))['s'] or 0
    completed_count = completed_orders.count()
    avg_price = round(total_revenue / completed_count, 2) if completed_count > 0 else 0

    top_clients = Client.objects.annotate(
        orders_count=Count('orders', filter=Q(
            orders__created_at__range=(start_dt, end_dt)
        )),
        total_spent=Sum('orders__price', filter=Q(
            orders__status='completed',
            orders__created_at__range=(start_dt, end_dt)
        ))
    ).filter(orders_count__gt=0).order_by('-total_spent')[:5]

    context = {
        'period': period,
        'days': days,
        'date_from': date_from,
        'date_to': date_to,
        'date_from_str': date_from.strftime('%Y-%m-%d'),
        'date_to_str': date_to.strftime('%Y-%m-%d'),
        'total_orders': total_orders_count,
        'completed': completed_count,
        'total_revenue': total_revenue,
        'avg_price': avg_price,
        'by_status': by_status,
        'by_master': by_master,
        'top_clients': top_clients,
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_data),
        'orders_count_data': json.dumps(orders_count_data),
        'status_labels': json.dumps(list(by_status.keys())),
        'status_counts': json.dumps(list(by_status.values())),
        'period_choices': [('7','7 днів'),('30','30 днів'),('90','90 днів'),('365','Рік')],
    }

    return render(request, 'dashboard/reports.html', context)

@login_required
def admin_view(request):
    if not request.user.is_staff: return redirect('dashboard:home')
    users=User.objects.select_related('employee').order_by('-date_joined')
    msg=None
    if request.method=='POST':
        action=request.POST.get('action')
        if action=='create_user':
            username=request.POST.get('username','').strip()
            password=request.POST.get('password','').strip()
            role=request.POST.get('role','master')
            emp_name=request.POST.get('emp_name','').strip()
            if username and password:
                if not User.objects.filter(username=username).exists():
                    u=User.objects.create_user(username=username,password=password)
                    Employee.objects.create(user=u,name=emp_name or username,role=role)
                    msg=f'Користувача {username} створено'
                else: msg='Такий логін вже існує'
        elif action=='toggle_active':
            u=get_object_or_404(User,pk=request.POST.get('user_id'))
            if u!=request.user: u.is_active=not u.is_active; u.save(); msg=f'Статус {u.username} змінено'
        elif action=='reset_password':
            u=get_object_or_404(User,pk=request.POST.get('user_id'))
            pwd=request.POST.get('new_password','').strip()
            if pwd: u.set_password(pwd); u.save(); msg=f'Пароль {u.username} оновлено'
        return redirect('dashboard:admin')
    return render(request,'dashboard/admin.html',{'users':users,'employees':Employee.objects.select_related('user'),'msg':msg,'roles':Employee.ROLE_CHOICES})

def login_view(request):
    if request.user.is_authenticated: return redirect('dashboard:home')
    error=None
    if request.method=='POST':
        from django.contrib.auth import authenticate,login
        user=authenticate(request,username=request.POST.get('username',''),password=request.POST.get('password',''))
        if user: login(request,user); return redirect('dashboard:home')
        error='Невірний логін або пароль'
    return render(request,'dashboard/login.html',{'error':error})

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('dashboard:login')
