"""
Моделі - ПРОСТО І ЗРОЗУМІЛО
Всі моделі тут для зручності
"""
from django.db import models
from django.contrib.auth.models import User
import random
import string

def generate_order_number():
    """Генерує номер типу RM12345678"""
    return 'RM' + ''.join(random.choices(string.digits, k=8))


class Client(models.Model):
    """Клієнт"""
    name = models.CharField(max_length=200, verbose_name="Ім'я")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Клієнт"
        verbose_name_plural = "Клієнти"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Employee(models.Model):
    """Співробітник - прив'язаний до User"""
    ROLE_CHOICES = [
        ('admin', 'Адміністратор'),
        ('master', 'Майстер'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    name = models.CharField(max_length=200, verbose_name="Ім'я")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='master')
    
    class Meta:
        verbose_name = "Співробітник"
        verbose_name_plural = "Співробітники"
    
    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"


class Order(models.Model):
    """Замовлення на ремонт"""
    STATUS_CHOICES = [
        ('new', 'Нова'),
        ('in_progress', 'В роботі'),
        ('ready', 'Готова'),
        ('completed', 'Видана'),
        ('cancelled', 'Скасована'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, default=generate_order_number)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    device = models.CharField(max_length=200, verbose_name="Пристрій")
    problem = models.TextField(verbose_name="Проблема")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_master = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'role': 'master'}
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Дедлайн
    deadline = models.DateField(
        verbose_name="Дедлайн виконання",
        null=True,
        blank=True,
        help_text="Планова дата завершення ремонту"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Генерація номера
        if not self.order_number:
            import time
            self.order_number = f"RM{int(time.time())}"
        
        # АВТОМАТИЧНЕ ВИДАЛЕННЯ ДЕДЛАЙНУ
        # Якщо "Видана" або "Скасована" - видалити дедлайн
        if self.status in ['completed', 'cancelled']:
            self.deadline = None
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.order_number} - {self.device}"
    
    def get_status_stage(self):
        """Повертає індекс поточного статусу для порівняння"""
        stages = [s[0] for s in self.STATUS_CHOICES]
        try:
            return stages.index(self.status)
        except ValueError:
            return 0


class Comment(models.Model):
    """Коментар майстра до замовлення"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField(verbose_name="Текст коментаря")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Коментар"
        verbose_name_plural = "Коментарі"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Коментар до {self.order.order_number}"


class Service(models.Model):
    """Послуга сервісного центру — ціни та умови керуються через адмін"""
    slug        = models.SlugField(max_length=50, unique=True, verbose_name="Slug")
    name        = models.CharField(max_length=200, verbose_name="Назва")
    label       = models.CharField(max_length=100, verbose_name="Коротка назва (для бейджа)")
    icon        = models.CharField(max_length=60, verbose_name="Іконка Font Awesome", help_text="Наприклад: fa-mobile-alt")
    description = models.TextField(verbose_name="Опис послуги")
    price_display = models.CharField(max_length=60, verbose_name="Ціна (текст)", help_text="Наприклад: від 250 ₴")
    price_from  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Ціна від (₴)", help_text="Числове значення для сортування")
    time_estimate = models.CharField(max_length=100, verbose_name="Час виконання", help_text="Наприклад: 30 хв – 2 год")
    warranty    = models.CharField(max_length=100, verbose_name="Гарантія", help_text="Наприклад: 12 місяців")
    features    = models.TextField(verbose_name="Що входить", help_text="По одному пункту на рядок")
    is_active   = models.BooleanField(default=True, verbose_name="Активна")
    sort_order  = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Послуга"
        verbose_name_plural = "Послуги"
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.name} — {self.price_display}"

    def get_features_list(self):
        return [f.strip() for f in self.features.split('\n') if f.strip()]


class Notification(models.Model):
    """Повідомлення про дедлайни"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='notifications')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField(verbose_name="Повідомлення")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Повідомлення"
        verbose_name_plural = "Повідомлення"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee.name}: {self.message[:50]}"
