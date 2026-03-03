"""
Management команда для завантаження демо-даних
Файл: dashboard/management/commands/load_demo_data.py

Використання:
python manage.py load_demo_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from orders.models import Order, Client, Employee
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Завантажує демонстраційні дані для диплому'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🚀 Завантаження демо-даних...'))
        
        # Видалити старі дані (опціонально)
        confirm = input('Видалити всі існуючі заявки? (y/n): ')
        if confirm.lower() == 'y':
            Order.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Старі заявки видалено'))
        
        # Створити клієнтів
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
                self.stdout.write(f'  ✓ {client.name}')
        
        # Створити майстрів
        if not Employee.objects.filter(role='master').exists():
            self.stdout.write('\n📝 Створення майстрів...')
            
            # Майстер 1
            user1, _ = User.objects.get_or_create(
                username='master_alex',
                defaults={'email': 'alex@fixflow.ua'}
            )
            if not hasattr(user1, 'password') or not user1.password:
                user1.set_password('master123')
                user1.save()
            
            master1, created = Employee.objects.get_or_create(
                user=user1,
                defaults={'name': 'Олександр Майстренко', 'role': 'master'}
            )
            if created:
                self.stdout.write(f'  ✓ {master1.name}')
            
            # Майстер 2
            user2, _ = User.objects.get_or_create(
                username='master_sergiy',
                defaults={'email': 'sergiy@fixflow.ua'}
            )
            if not hasattr(user2, 'password') or not user2.password:
                user2.set_password('master123')
                user2.save()
            
            master2, created = Employee.objects.get_or_create(
                user=user2,
                defaults={'name': 'Сергій Ремонтник', 'role': 'master'}
            )
            if created:
                self.stdout.write(f'  ✓ {master2.name}')
        
        masters = list(Employee.objects.filter(role='master'))
        
        # Створити реалістичні заявки
        self.stdout.write('\n📦 Створення заявок...')
        
        devices = [
            "iPhone 14 Pro", "iPhone 13", "iPhone 12 Pro Max", "iPhone 15",
            "Samsung Galaxy S23 Ultra", "Samsung Galaxy A54", "Samsung Galaxy S24",
            "MacBook Pro 14", "MacBook Air M2", "iPad Pro 12.9",
            "AirPods Pro 2", "Apple Watch Series 9", "iPad Air",
            "MacBook Pro 16", "iMac 24"
        ]
        
        problems = [
            "Не вмикається, можливо проблема з материнською платою",
            "Розбитий екран, потрібна повна заміна дисплею",
            "Не заряджається, перевірити порт Lightning",
            "Батарея швидко розряджається, потрібна заміна",
            "Не працює камера, помилка при запуску",
            "Немає звуку в динаміках",
            "Потрібна заміна скла та тачскріну",
            "Апгрейд оперативної пам'яті до 16GB",
            "Повільно працює, потрібне чищення",
            "Проблеми з Wi-Fi модулем",
            "Потрібна заміна клавіатури",
            "Перегрівається при роботі",
            "Не працює Face ID",
            "Проблеми з підсвіткою екрану",
            "Потрібна діагностика системи охолодження"
        ]
        
        # Розподіл статусів для реалістичності
        statuses_distribution = (
            ['new'] * 5 +           # 5 нових
            ['in_progress'] * 12 +  # 12 в роботі
            ['ready'] * 8 +         # 8 готових
            ['completed'] * 20 +    # 20 завершених
            ['cancelled'] * 2       # 2 скасовані
        )
        random.shuffle(statuses_distribution)
        
        today = timezone.now()
        orders_created = 0
        
        for i in range(47):  # Створюємо 47 заявок
            # Випадкова дата за останні 35 днів
            days_ago = random.randint(0, 34)
            created_date = today - timedelta(days=days_ago)
            
            client = random.choice(clients)
            device = random.choice(devices)
            problem = random.choice(problems)
            status = statuses_distribution[i]
            
            # Ціна залежить від пристрою та статусу
            price = None
            if status in ['completed', 'ready']:
                if 'MacBook' in device or 'iMac' in device:
                    price = random.randint(2000, 8000)
                elif 'iPad' in device:
                    price = random.randint(1500, 4000)
                elif 'iPhone' in device:
                    price = random.randint(800, 3500)
                elif 'Watch' in device or 'AirPods' in device:
                    price = random.randint(500, 1500)
                else:
                    price = random.randint(1000, 5000)
            
            # Призначити майстра
            assigned_master = None
            if status in ['in_progress', 'ready', 'completed'] and masters:
                assigned_master = random.choice(masters)
            
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
            
            # Прогрес бар
            if orders_created % 10 == 0:
                self.stdout.write(f'  {orders_created}/47 заявок створено...')
        
        # Підсумок
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('\n✅ ДЕМО-ДАНІ УСПІШНО ЗАВАНТАЖЕНО!\n'))
        self.stdout.write('='*50)
        self.stdout.write(f'\n📊 Статистика:')
        self.stdout.write(f'   • Клієнтів: {Client.objects.count()}')
        self.stdout.write(f'   • Майстрів: {Employee.objects.filter(role="master").count()}')
        self.stdout.write(f'   • Заявок: {Order.objects.count()}')
        self.stdout.write(f'     - Нових: {Order.objects.filter(status="new").count()}')
        self.stdout.write(f'     - В роботі: {Order.objects.filter(status="in_progress").count()}')
        self.stdout.write(f'     - Готові: {Order.objects.filter(status="ready").count()}')
        self.stdout.write(f'     - Завершені: {Order.objects.filter(status="completed").count()}')
        self.stdout.write(f'     - Скасовані: {Order.objects.filter(status="cancelled").count()}')
        
        from django.db.models import Sum
        total_revenue = Order.objects.filter(status='completed').aggregate(s=Sum('price'))['s'] or 0
        completed_count = Order.objects.filter(status='completed').count()
        avg_price = round(total_revenue / completed_count, 2) if completed_count else 0
        
        self.stdout.write(f'\n💰 Фінанси:')
        self.stdout.write(f'   • Загальна виручка: {total_revenue} ₴')
        self.stdout.write(f'   • Середній чек: {avg_price} ₴')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Тепер відкрий дашборд - побачиш красиві графіки!'))
        self.stdout.write(self.style.WARNING('   Логін майстрів: master_alex / master_sergiy'))
        self.stdout.write(self.style.WARNING('   Пароль: master123\n'))
