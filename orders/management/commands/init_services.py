from django.core.management.base import BaseCommand
from orders.models import Service


SERVICES = [
    {
        'slug': 'phones',
        'name': 'Ремонт смартфонів',
        'label': 'Смартфони',
        'icon': 'fa-mobile-alt',
        'description': 'Професійне відновлення смартфонів будь-якої складності. Працюємо з усіма моделями iPhone, Samsung, Xiaomi, Huawei та інших брендів.',
        'price_display': 'від 250 ₴',
        'price_from': 250,
        'time_estimate': '30 хв – 2 год',
        'warranty': '12 місяців',
        'features': (
            'Заміна екрана (OLED / LCD / AMOLED)\n'
            'Заміна акумулятора\n'
            'Ремонт після залиття водою\n'
            'Заміна камери та мікрофона\n'
            'Ремонт роз\'ємів та кнопок\n'
            'Відновлення після механічних пошкоджень'
        ),
        'sort_order': 1,
    },
    {
        'slug': 'laptops',
        'name': 'Ремонт ноутбуків',
        'label': 'Ноутбуки',
        'icon': 'fa-laptop',
        'description': 'Комплексне обслуговування ноутбуків усіх брендів: Apple MacBook, ASUS, Dell, HP, Lenovo, Acer та інших. Мікропайка та відновлення материнських плат.',
        'price_display': 'від 400 ₴',
        'price_from': 400,
        'time_estimate': '1 – 48 год',
        'warranty': '12 місяців',
        'features': (
            'Чистка та заміна термопасти\n'
            'Ремонт та заміна матриці\n'
            'Заміна клавіатури\n'
            'Ремонт материнської плати (мікропайка)\n'
            'Апгрейд RAM та SSD\n'
            'Заміна акумулятора'
        ),
        'sort_order': 2,
    },
    {
        'slug': 'pc',
        'name': 'Ремонт ПК',
        'label': 'ПК',
        'icon': 'fa-desktop',
        'description': 'Діагностика, ремонт та модернізація стаціонарних комп\'ютерів будь-якої конфігурації. Gaming PC, робочі станції, сервери.',
        'price_display': 'від 300 ₴',
        'price_from': 300,
        'time_estimate': '1 – 24 год',
        'warranty': '12 місяців',
        'features': (
            'Апгрейд відеокарти, RAM, CPU\n'
            'Збірка ПК під ключ за бюджетом\n'
            'Встановлення Windows / Linux\n'
            'Видалення вірусів та оптимізація\n'
            'Ремонт блоку живлення\n'
            'Налаштування охолодження'
        ),
        'sort_order': 3,
    },
    {
        'slug': 'data',
        'name': 'Відновлення даних',
        'label': 'Відновлення',
        'icon': 'fa-hdd',
        'description': 'Професійне відновлення інформації з пошкоджених носіїв: HDD, SSD, флешки, карти пам\'яті. Навіть після фізичного пошкодження.',
        'price_display': 'від 800 ₴',
        'price_from': 800,
        'time_estimate': '2 – 72 год',
        'warranty': 'Гарантія результату',
        'features': (
            'Відновлення з HDD та SSD\n'
            'Відновлення з флешок та карт пам\'яті\n'
            'Відновлення після форматування\n'
            'Відновлення після вірусного ураження\n'
            'Відновлення з механічно пошкоджених носіїв\n'
            'Безкоштовна діагностика'
        ),
        'sort_order': 4,
    },
    {
        'slug': 'software',
        'name': 'Налаштування ПЗ',
        'label': 'Програмне ПЗ',
        'icon': 'fa-cog',
        'description': 'Оптимізація ОС, встановлення програм, повне видалення вірусів та шкідливого ПЗ. Працюємо з Windows та macOS.',
        'price_display': 'від 200 ₴',
        'price_from': 200,
        'time_estimate': '30 хв – 3 год',
        'warranty': '3 місяці',
        'features': (
            'Встановлення та активація Windows / macOS\n'
            'Видалення вірусів та рекламного ПЗ\n'
            'Оптимізація швидкодії системи\n'
            'Встановлення та налаштування програм\n'
            'Налаштування мережі та Інтернету\n'
            'Резервне копіювання даних'
        ),
        'sort_order': 5,
    },
    {
        'slug': 'express',
        'name': 'Експрес-сервіс',
        'label': 'Терміново',
        'icon': 'fa-bolt',
        'description': 'Терміновий ремонт у пріоритетному порядку без черги. Ваш пристрій беруть у роботу негайно. Доступно щодня, у вихідні та святкові дні.',
        'price_display': '+50% до ціни',
        'price_from': None,
        'time_estimate': '30 хв – 3 год',
        'warranty': '12 місяців',
        'features': (
            'Пріоритетна обробка без черги\n'
            'Виконання у день звернення\n'
            'Доступно 7 днів на тиждень\n'
            'Для всіх видів ремонту\n'
            'SMS-повідомлення про готовність\n'
            'Та сама гарантія якості'
        ),
        'sort_order': 6,
    },
]


class Command(BaseCommand):
    help = 'Заповнює базу початковими послугами сервісного центру'

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for data in SERVICES:
            obj, is_new = Service.objects.update_or_create(
                slug=data['slug'],
                defaults=data,
            )
            if is_new:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  + Створено: {obj.name}'))
            else:
                updated += 1
                self.stdout.write(f'  ~ Оновлено: {obj.name}')

        self.stdout.write(self.style.SUCCESS(
            f'\nГотово! Створено: {created}, оновлено: {updated} послуг.'
        ))
        self.stdout.write(
            'Тепер відкрийте /admin/ -> Послуги i змінюйте ціни прямо там.'
        )
