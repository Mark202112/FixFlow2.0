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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.device}"
    
    def get_status_stage(self):
        """Повертає індекс поточного статусу для порівняння"""
        stages = [s[0] for s in self.STATUS_CHOICES]
        try:
            return stages.index(self.status)
        except ValueError:
            return 0
