"""
Скрипт для створення тестових даних - ВИПРАВЛЕНА ВЕРСІЯ
Створює дані за останні 30 днів від СЬОГОДНІ!

Запуск:
python manage.py shell < FIXED_create_test_data.py
"""

from orders.models import Order, Client, Employee
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

print("=" * 60)
print("🚀 СТВОРЕННЯ ТЕСТОВИХ ДАНИХ (ВИПРАВЛЕНА ВЕРСІЯ)")
print("=" * 60)

# ВИДАЛИТИ всі старі заявки
print("\n⚠️  Видалення старих даних...")
Order.objects.all().delete()
print("✓ Старі заявки видалено")

# Створити клієнтів
print("\n📝 Створення клієнтів...")
clients_data = [
    {"name": "Іван Петренко", "phone": "0501234567", "email": "ivan@gmail.com"},
    {"name": "Марія Коваленко", "phone": "0671234567", "email": "maria@ukr.net"},
    {"name": "Олег Сидоренко", "phone": "0931234567", "email": "oleg@meta.ua"},
    {"name": "Анна Мельник", "phone": "0631234567", "email": "anna@gmail.com"},
    {"name": "Дмитро Шевченко", "phone": "0991234567", "email": "dmytro@i.ua"},
    {"name": "Наталія Іваненко", "phone": "0951234567", "email": "natalia@gmail.com"},
    {"name": "Володимир Бойко", "phone": "0661234567", "email": "vova@ukr.net"},
    {"name": "Олена Ткаченко", "phone": "0731234567", "email": "olena@meta.ua"},
]

clients = []
for data in clients_data:
    client, created = Client.objects.get_or_create(
        phone=data["phone"],
        defaults={"name": data["name"], "email": data["email"]}
    )
    clients.append(client)
    if created:
        print(f"  ✓ {client.name}")

# Створити майстрів якщо немає
print("\n👨‍🔧 Перевірка майстрів...")
if not Employee.objects.filter(role='master').exists():
    user1, _ = User.objects.get_or_create(username='master_alex', defaults={'email': 'alex@fixflow.ua'})
    user1.set_password('master123')
    user1.save()
    
    user2, _ = User.objects.get_or_create(username='master_sergiy', defaults={'email': 'sergiy@fixflow.ua'})
    user2.set_password('master123')
    user2.save()
    
    master1, _ = Employee.objects.get_or_create(user=user1, defaults={'name': 'Олександр Майстренко', 'role': 'master'})
    master2, _ = Employee.objects.get_or_create(user=user2, defaults={'name': 'Сергій Ремонтник', 'role': 'master'})
    print(f"  ✓ {master1.name}")
    print(f"  ✓ {master2.name}")
else:
    print(f"  ✓ Майстри вже існують")

masters = list(Employee.objects.filter(role='master'))

# ВАЖЛИВО: Створити заявки ЗА ОСТАННІ 30 ДНІВ ВІД СЬОГОДНІ
print("\n📦 Створення заявок...")

devices = [
    "iPhone 14 Pro", "iPhone 13", "iPhone 12 Pro Max", "iPhone 15",
    "Samsung Galaxy S23", "Samsung A54", "Samsung S24",
    "MacBook Pro 14", "MacBook Air M2", "iPad Pro",
    "AirPods Pro", "Apple Watch S9"
]

problems = [
    "Не вмикається, потрібна діагностика",
    "Розбитий екран, заміна дисплею",
    "Не заряджається, перевірити порт",
    "Батарея швидко сідає, потрібна заміна",
    "Не працює камера",
    "Немає звуку в динаміках",
    "Потрібна заміна скла",
    "Апгрейд пам'яті до 16GB",
    "Повільно працює, чищення",
    "Проблеми з Wi-Fi"
]

# Розподіл статусів
statuses_distribution = (
    ['new'] * 5 +           # 5 нових
    ['in_progress'] * 12 +  # 12 в роботі
    ['ready'] * 8 +         # 8 готових
    ['completed'] * 20 +    # 20 завершених
    ['cancelled'] * 2       # 2 скасовані
)
random.shuffle(statuses_distribution)

# КРИТИЧНО: Отримати СЬОГОДНІШНЮ дату
today = timezone.now()
print(f"\n📅 Сьогоднішня дата: {today.date()}")
print(f"📅 Створюю дані з {(today - timedelta(days=29)).date()} по {today.date()}")

orders_created = 0

for i in range(47):
    # Випадкова дата за ОСТАННІ 30 днів від СЬОГОДНІ
    days_ago = random.randint(0, 29)
    created_date = today - timedelta(days=days_ago)
    
    client = random.choice(clients)
    device = random.choice(devices)
    problem = random.choice(problems)
    status = statuses_distribution[i]
    
    # Ціна залежить від статусу
    price = None
    if status in ['completed', 'ready']:
        if 'MacBook' in device or 'iMac' in device:
            price = random.randint(2000, 8000)
        elif 'iPad' in device:
            price = random.randint(1500, 4000)
        elif 'iPhone' in device:
            price = random.randint(800, 3500)
        else:
            price = random.randint(500, 1500)
    
    # Майстер
    assigned_master = None
    if status in ['in_progress', 'ready', 'completed'] and masters:
        assigned_master = random.choice(masters)
    
    # Створити заявку
    order = Order.objects.create(
        client=client,
        device=device,
        problem=problem,
        status=status,
        price=price,
        assigned_master=assigned_master,
        created_at=created_date
    )
    
    orders_created += 1
    
    if orders_created % 10 == 0:
        print(f"  {orders_created}/47 створено...")

# Підсумок
print("\n" + "=" * 60)
print("✅ ДАНІ УСПІШНО СТВОРЕНО!")
print("=" * 60)

from django.db.models import Sum

print(f"\n📊 Статистика:")
print(f"   • Клієнтів: {Client.objects.count()}")
print(f"   • Майстрів: {Employee.objects.filter(role='master').count()}")
print(f"   • Заявок: {Order.objects.count()}")
print(f"     - Нових: {Order.objects.filter(status='new').count()}")
print(f"     - В роботі: {Order.objects.filter(status='in_progress').count()}")
print(f"     - Готові: {Order.objects.filter(status='ready').count()}")
print(f"     - Завершені: {Order.objects.filter(status='completed').count()}")

total_revenue = Order.objects.filter(status='completed').aggregate(s=Sum('price'))['s'] or 0
completed_count = Order.objects.filter(status='completed').count()
avg_price = round(total_revenue / completed_count, 2) if completed_count else 0

print(f"\n💰 Фінанси:")
print(f"   • Виручка: {total_revenue} ₴")
print(f"   • Середній чек: {avg_price} ₴")

# Показати діапазон дат
oldest = Order.objects.order_by('created_at').first()
newest = Order.objects.order_by('-created_at').first()

if oldest and newest:
    print(f"\n📅 Діапазон заявок:")
    print(f"   Від: {oldest.created_at.date()}")
    print(f"   До: {newest.created_at.date()}")

print("\n🎉 Тепер відкрий дашборд і побачиш дані!")
print("   Звіти за 7 днів: буде ~11 заявок")
print("   Звіти за 30 днів: буде 47 заявок")
print("\n" + "=" * 60 + "\n")
