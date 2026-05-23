# FixFlow — Повний мануал з встановлення та запуску

**Система автоматизації ремонтної майстерні**

---

## Зміст

1. [Що таке FixFlow](#1-що-таке-fixflow)
2. [Системні вимоги](#2-системні-вимоги)
3. [Крок 1 — Встановлення Python](#крок-1--встановлення-python)
4. [Крок 2 — Завантаження проекту](#крок-2--завантаження-проекту)
5. [Крок 3 — Віртуальне середовище](#крок-3--віртуальне-середовище)
6. [Крок 4 — Встановлення залежностей](#крок-4--встановлення-залежностей)
7. [Крок 5 — Налаштування бази даних](#крок-5--налаштування-бази-даних)
8. [Крок 6 — Файл конфігурації .env](#крок-6--файл-конфігурації-env)
9. [Крок 7 — Міграції бази даних](#крок-7--міграції-бази-даних)
10. [Крок 8 — Ініціалізація сервісів](#крок-8--ініціалізація-сервісів)
11. [Крок 9 — Створення адміністратора](#крок-9--створення-адміністратора)
12. [Крок 10 — Створення майстра](#крок-10--створення-майстра)
13. [Крок 11 — Запуск сайту](#крок-11--запуск-сайту)
14. [Як користуватись системою](#як-користуватись-системою)
15. [Часті помилки](#часті-помилки)
16. [Деплой на сервер](#деплой-на-сервер)

---

## 1. Що таке FixFlow

FixFlow — це веб-система для автоматизації роботи ремонтної майстерні. Складається з двох частин:

- **Публічний сайт** — клієнт може залишити заявку на ремонт і перевірити статус свого замовлення за номером
- **Dashboard для персоналу** — майстри та адміністратори бачать замовлення, керують клієнтами, переглядають звіти та календар дедлайнів

**Технології:** Python 3, Django 5, MySQL, HTML/CSS

---

## 2. Системні вимоги

Перед початком переконайся, що на комп'ютері є:

| Програма | Мінімальна версія | Де завантажити |
|---|---|---|
| Python | 3.10 або новіший | https://www.python.org/downloads/ |
| pip | встановлюється разом з Python | — |
| MySQL Server | 8.0 або новіший | https://dev.mysql.com/downloads/mysql/ |
| Git (необов'язково) | будь-яка | https://git-scm.com/downloads |

> Якщо не хочеш встановлювати MySQL — є простіший варіант з SQLite, описаний у [Кроці 5](#крок-5--налаштування-бази-даних).

---

## Крок 1 — Встановлення Python

### Windows

1. Відкрий https://www.python.org/downloads/
2. Завантаж Python 3.11 або новіший (кнопка "Download Python 3.x.x")
3. Запусти інсталятор
4. **ВАЖЛИВО:** На першому екрані постав галочку **"Add Python to PATH"**
5. Натисни "Install Now"

**Перевірка встановлення** — відкрий командний рядок (Win+R → `cmd`) і введи:

```
python --version
```

Повинно вивести щось на кшталт: `Python 3.11.9`

```
pip --version
```

Повинно вивести щось на кшталт: `pip 24.0 from ...`

### macOS / Linux

```bash
# macOS (через Homebrew)
brew install python@3.11

# Ubuntu / Debian
sudo apt update
sudo apt install python3.11 python3-pip
```

---

## Крок 2 — Завантаження проекту

### Варіант А — через Git

```bash
git clone <посилання-на-репозиторій>
cd workshop
```

### Варіант Б — через ZIP-архів

1. Завантаж ZIP-архів з проектом
2. Розпакуй у зручне місце, наприклад: `C:\Projects\workshop`
3. Відкрий командний рядок і перейди в папку проекту:

```
cd C:\Projects\workshop
```

**Перевірка:** введи `dir` (Windows) або `ls` (macOS/Linux) — маєш бачити файли `manage.py`, `requirements.txt` тощо.

---

## Крок 3 — Віртуальне середовище

Віртуальне середовище — це ізольований простір для Python-бібліотек проекту. Це гарна практика, яка дозволяє уникнути конфліктів між проектами.

**Створення:**

```bash
python -m venv venv
```

**Активація:**

```bash
# Windows (командний рядок cmd)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

Після активації на початку рядка з'явиться `(venv)`:

```
(venv) C:\Projects\workshop>
```

> Щоразу при роботі з проектом — спочатку активуй середовище. Якщо закрив термінал — потрібно активувати знову.

---

## Крок 4 — Встановлення залежностей

Переконайся, що `(venv)` активований, і виконай:

```bash
pip install -r requirements.txt
```

Ця команда встановить:
- `Django 5.0` — фреймворк
- `PyMySQL 1.1.1` — драйвер для підключення до MySQL
- `python-dotenv` — зчитування налаштувань з `.env` файлу
- `gunicorn` — сервер для продакшн-деплою

**Перевірка:**

```bash
pip list
```

Маєш бачити Django, PyMySQL та інші пакети у списку.

---

## Крок 5 — Налаштування бази даних

Є два варіанти: **MySQL** (рекомендований) або **SQLite** (простіший, тільки для локальної розробки).

---

### Варіант А — MySQL (рекомендований)

#### 1. Встановлення MySQL Server

Завантаж і встанови MySQL з https://dev.mysql.com/downloads/mysql/

Під час встановлення запам'ятай або запиши **root-пароль**.

#### 2. Підключення до MySQL

Відкрий MySQL командний рядок або MySQL Workbench і виконай наступні SQL-команди:

```sql
-- Створюємо базу даних
CREATE DATABASE fixflow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Створюємо користувача
CREATE USER 'fixflow_user'@'localhost' IDENTIFIED BY 'FixFlow2024';

-- Надаємо права
GRANT ALL PRIVILEGES ON fixflow.* TO 'fixflow_user'@'localhost';
FLUSH PRIVILEGES;
```

> Назву бази (`fixflow`), ім'я користувача (`fixflow_user`) і пароль (`FixFlow2024`) можна змінити — але тоді потрібно оновити і файл `config/settings.py`.

#### 3. Перевірка в settings.py

Відкрий файл `config/settings.py` і переконайся, що налаштування збігаються:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fixflow',           # назва бази
        'USER': 'fixflow_user',      # ім'я користувача
        'PASSWORD': 'FixFlow2024',   # пароль
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

---

### Варіант Б — SQLite (простіший)

SQLite не потребує окремого сервера — база даних зберігається в одному файлі.

Відкрий `config/settings.py`, знайди блок `DATABASES` і **заміни його повністю** на:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Також **видали перші 3 рядки** файлу (вони потрібні лише для MySQL):

```python
# ВИДАЛИ ЦІ 3 РЯДКИ:
import pymysql
pymysql.version_info = (1, 4, 6, 'final', 0)
pymysql.install_as_MySQLdb()
```

---

## Крок 6 — Файл конфігурації .env

У папці проекту є файл `.env.example` — це шаблон конфігурації. Потрібно створити з нього файл `.env`.

**Windows:**

```
copy .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Тепер відкрий `.env` у будь-якому текстовому редакторі і заповни:

```env
SECRET_KEY=придумай-довгий-рядок-символів-тут
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Як згенерувати SECRET_KEY:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Скопіюй результат і встав замість `придумай-довгий-рядок-символів-тут`.

---

## Крок 7 — Міграції бази даних

Міграції — це команда, яка створює всі необхідні таблиці в базі даних.

```bash
python manage.py migrate
```

Якщо все налаштовано правильно, побачиш список виконаних міграцій:

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, orders, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying orders.0001_initial... OK
```

> Якщо з'явилась помилка — перевір розділ [Часті помилки](#часті-помилки).

---

## Крок 8 — Ініціалізація сервісів

Ця команда заповнює каталог послуг початковими даними (ремонт телефонів, ноутбуків, ПК тощо):

```bash
python manage.py init_services
```

> Виконується лише **один раз** при першому запуску. Якщо запустиш повторно — нічого не зламається, просто ігноруй.

---

## Крок 9 — Створення адміністратора

Адміністратор — це головний користувач системи, у якого є доступ до всіх функцій.

```bash
python manage.py createsuperuser
```

Система запитає:

```
Username: admin
Email address: (можна залишити порожнім, просто натисни Enter)
Password: ****
Password (again): ****
Superuser created successfully.
```

Тепер потрібно прив'язати цього користувача до профілю майстра/адміна в системі:

```bash
python manage.py shell
```

У інтерактивному режимі Python виконай (по одному рядку, Enter після кожного):

```python
from django.contrib.auth.models import User
from orders.models import Employee

user = User.objects.get(username='admin')
Employee.objects.create(user=user, name='Адміністратор', role='admin')
exit()
```

> Замість `'admin'` вкажи те ім'я, яке ти вводив при `createsuperuser`. Замість `'Адміністратор'` — реальне ім'я.

---

## Крок 10 — Створення майстра

Майстер — це співробітник, який бачить і обробляє замовлення. Можна створити кілька майстрів.

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from orders.models import Employee

# Створити нового майстра (ім'я, email, пароль)
user = User.objects.create_user('ivan_master', '', 'пароль123', is_staff=True)
Employee.objects.create(user=user, name='Іван Майстренко', role='master')
exit()
```

> Замість `'ivan_master'` — логін для входу.
> Замість `'пароль123'` — надійний пароль.
> Замість `'Іван Майстренко'` — реальне ім'я, яке буде відображатись у системі.

**Роль `role`** може бути:
- `'master'` — майстер, бачить і обробляє замовлення
- `'admin'` — адміністратор, має доступ до всіх функцій включно з управлінням персоналом

---

## Крок 11 — Запуск сайту

```bash
python manage.py runserver
```

Відкрий браузер і перейди на:

| Адреса | Що це |
|---|---|
| http://127.0.0.1:8000/ | Публічний сайт (для клієнтів) |
| http://127.0.0.1:8000/dashboard/ | Dashboard для персоналу |
| http://127.0.0.1:8000/admin/ | Django Admin-панель |

Для зупинки сервера натисни `Ctrl + C` у терміналі.

---

## Як користуватись системою

### Клієнт (публічний сайт)

1. Відкриває `http://127.0.0.1:8000/`
2. Натискає **"Залишити заявку"**
3. Вводить ім'я, телефон, тип пристрою та опис проблеми
4. Отримує **номер замовлення** (наприклад: `RM12345678`)
5. Пізніше може перевірити статус за цим номером

### Майстер / Адміністратор (Dashboard)

1. Відкриває `http://127.0.0.1:8000/dashboard/`
2. Вводить логін і пароль, які були створені на [Кроці 9](#крок-9--створення-адміністратора) або [Кроці 10](#крок-10--створення-майстра)
3. Бачить дашборд зі статистикою

**Що є в Dashboard:**

| Розділ | Опис |
|---|---|
| Головна | Статистика за день, останні замовлення |
| Замовлення | Повний список, фільтри за статусом, пошук |
| Клієнти | Список клієнтів, їх замовлення та витрати |
| Календар | Дедлайни замовлень по датах |
| Звіти | Виручка за 7 / 30 / 90 / 365 днів |
| Адмін-панель | Управління майстрами (тільки для role='admin') |

**Статуси замовлень:**

| Статус | Значення |
|---|---|
| Нове | Щойно надійшло, ще не взяте в роботу |
| В роботі | Майстер працює над ремонтом |
| Готово | Ремонт завершено, чекає клієнта |
| Виконано | Клієнт забрав пристрій |
| Скасовано | Замовлення скасоване |

---

## Часті помилки

### "No module named 'pymysql'"

Не встановлений драйвер MySQL. Виконай:

```bash
pip install PyMySQL==1.1.1
```

---

### "django.db.utils.OperationalError: (2003, Can't connect to MySQL server)"

MySQL сервер не запущений або неправильні дані підключення.

- Перевір, чи запущений MySQL (у Windows: Служби → MySQL)
- Перевір логін/пароль у `config/settings.py`
- Перевір, чи існує база даних `fixflow` (виконай команди з [Кроку 5](#варіант-а--mysql-рекомендований))

---

### "ModuleNotFoundError: No module named 'django'"

Не активоване віртуальне середовище або не встановлені залежності.

```bash
# Активуй середовище
venv\Scripts\activate         # Windows
source venv/bin/activate      # macOS/Linux

# Встанови залежності
pip install -r requirements.txt
```

---

### "That port is already in use"

Порт 8000 зайнятий іншим процесом. Запусти на іншому порту:

```bash
python manage.py runserver 8080
```

Потім відкривай `http://127.0.0.1:8080/`

---

### "Permission denied" при активації venv у PowerShell

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Після цього спробуй активацію знову.

---

### Порожній каталог послуг на сайті

Не виконана команда ініціалізації:

```bash
python manage.py init_services
```

---

### "You have unapplied migrations"

Не всі міграції застосовані. Виконай:

```bash
python manage.py migrate
```

---

## Деплой на сервер

> Цей розділ — для розгортання на реальному сервері (VPS / хостинг). Для локальної розробки він не потрібен.

### 1. Підготовка .env для продакшну

```env
SECRET_KEY=дуже-довгий-унікальний-рядок
DEBUG=False
ALLOWED_HOSTS=твій-домен.com,www.твій-домен.com
```

### 2. Збір статичних файлів

```bash
python manage.py collectstatic
```

Всі CSS, зображення зберуться у папку `staticfiles/`.

### 3. Запуск через Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### 4. Nginx як проксі (рекомендовано)

Налаштуй Nginx для роздачі статики та проксіювання запитів до Gunicorn. Приклад конфігурації:

```nginx
server {
    listen 80;
    server_name твій-домен.com;

    location /static/ {
        alias /шлях/до/проекту/staticfiles/;
    }

    location /media/ {
        alias /шлях/до/проекту/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Короткий підсумок команд

```bash
# Активація середовища (щоразу)
venv\Scripts\activate

# Встановлення залежностей (один раз)
pip install -r requirements.txt

# Міграції (один раз, або після змін у моделях)
python manage.py migrate

# Ініціалізація послуг (один раз)
python manage.py init_services

# Створення адміна (один раз)
python manage.py createsuperuser

# Запуск сервера
python manage.py runserver
```

---

*FixFlow — система автоматизації ремонтної майстерні. Django 5 | MySQL | Python 3*
