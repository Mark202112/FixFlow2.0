from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import json
from orders.models import Order, Client, Employee

def get_employee(request):
    try:
        return request.user.employee
    except Exception:
        return None

@login_required
def dashboard_home(request):
    orders  = Order.objects.select_related('client','assigned_master')
    today   = timezone.now().date()
    week_ago = today - timedelta(days=7)
    masters = Employee.objects.filter(role='master').annotate(
        active=Count('order', filter=Q(order__status='in_progress'))
    )
    chart_labels, chart_data = [], []
    for i in range(6,-1,-1):
        d = today - timedelta(days=i)
        chart_labels.append(d.strftime('%d.%m'))
        chart_data.append(orders.filter(created_at__date=d).count())
    context = {
        'employee':    get_employee(request),
        'total':       orders.count(),
        'new_orders':  orders.filter(status='new').count(),
        'in_progress': orders.filter(status='in_progress').count(),
        'ready':       orders.filter(status='ready').count(),
        'revenue':     orders.filter(status='completed').aggregate(s=Sum('price'))['s'] or 0,
        'week_orders': orders.filter(created_at__date__gte=week_ago).count(),
        'recent':      orders.order_by('-created_at')[:8],
        'masters':     masters,
        'chart_labels': json.dumps(chart_labels),
        'chart_data':   json.dumps(chart_data),
        'status_choices': Order.STATUS_CHOICES,
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
            order.save()

        elif action == 'add_comment':
            comment_text = request.POST.get('comment', '').strip()
            if comment_text:
                Comment.objects.create(
                    order=order,
                    author=get_employee(request),
                    text=comment_text
                )

        return redirect('dashboard:order_detail', order_number=order.order_number)

    return render(request, 'dashboard/order_detail.html', {
        'order':    order,
        'masters':  masters,
        'comments': comments,
    })

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
        client.email=request.POST.get('email',client.email).strip()
        client.save()
        return redirect('dashboard:client_detail',pk=pk)
    return render(request,'dashboard/client_detail.html',{'client':client,'orders':orders,'status_choices':Order.STATUS_CHOICES})

@login_required
def create_client(request):
    error=None
    if request.method=='POST':
        name=request.POST.get('name','').strip()
        phone=request.POST.get('phone','').strip()
        email=request.POST.get('email','').strip()
        if name and phone:
            if Client.objects.filter(phone=phone).exists(): error='Клієнт з таким номером вже існує'
            else:
                c=Client.objects.create(name=name,phone=phone,email=email)
                return redirect('dashboard:client_detail',pk=c.pk)
        else: error="Ім'я та телефон обов'язкові"
    return render(request,'dashboard/client_form.html',{'error':error})

@login_required
def calendar_view(request):
    today=timezone.now().date()
    month_start=today.replace(day=1)
    if today.month==12: month_end=today.replace(year=today.year+1,month=1,day=1)-timedelta(days=1)
    else: month_end=today.replace(month=today.month+1,day=1)-timedelta(days=1)
    orders=Order.objects.filter(created_at__date__gte=month_start,created_at__date__lte=month_end).select_related('client')
    colors={'new':'#007AFF','in_progress':'#ff9500','ready':'#34c759','completed':'#86868b','cancelled':'#ff3b30'}
    events=[{'id':o.order_number,'title':f'{o.device} — {o.client.name}','date':o.created_at.strftime('%Y-%m-%d'),'color':colors.get(o.status,'#007AFF'),'status':o.get_status_display()} for o in orders]
    return render(request,'dashboard/calendar.html',{'events_json':json.dumps(events),'today':today.strftime('%Y-%m-%d'),'month_orders':orders.count()})

@login_required
def reports_view(request):
    period=request.GET.get('period','30')
    try: days=int(period)
    except: days=30
    today=timezone.now().date()
    date_from=today-timedelta(days=days)
    orders=Order.objects.filter(created_at__date__gte=date_from)
    by_status={}
    for val,label in Order.STATUS_CHOICES: by_status[label]=orders.filter(status=val).count()
    by_master=Employee.objects.filter(role='master').annotate(
        done=Count('order',filter=Q(order__status__in=['ready','completed'],order__created_at__date__gte=date_from)),
        revenue=Sum('order__price',filter=Q(order__status='completed',order__created_at__date__gte=date_from))
    )
    revenue_labels,revenue_data=[],[]
    for i in range(days-1,-1,-1):
        d=today-timedelta(days=i)
        rev=orders.filter(created_at__date=d,status='completed').aggregate(s=Sum('price'))['s'] or 0
        revenue_labels.append(d.strftime('%d.%m'))
        revenue_data.append(float(rev))
    total_revenue=orders.filter(status='completed').aggregate(s=Sum('price'))['s'] or 0
    completed_count=orders.filter(status='completed').count()
    avg_price=round(total_revenue/completed_count,2) if completed_count else 0
    return render(request,'dashboard/reports.html',{
        'period':period,'days':days,'date_from':date_from,
        'total_orders':orders.count(),'completed':completed_count,
        'total_revenue':total_revenue,'avg_price':avg_price,
        'by_status':by_status,'by_master':by_master,
        'revenue_labels':json.dumps(revenue_labels),'revenue_data':json.dumps(revenue_data),
        'status_labels':json.dumps(list(by_status.keys())),'status_counts':json.dumps(list(by_status.values())),
        'period_choices': [('7','7 днів'),('30','30 днів'),('90','90 днів'),('365','Рік')],
    })

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
