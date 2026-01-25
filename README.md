# No Lose SaaS Platform

## 📋 Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Структура проекта](#структура-проекта)
3. [Технологический стек](#технологический-стек)
4. [Установка и запуск](#установка-и-запуск)
5. [Архитектура](#архитектура)
6. [API документация](#api-документация)
7. [Frontend страницы](#frontend-страницы)
8. [Database схема](#database-схема)
9. [Аутентификация](#аутентификация)
10. [Основные потоки](#основные-потоки)

---

## 🎯 Обзор проекта

**No Lose** — это полнофункциональная SaaS платформа с:

- ✅ Системой аутентификации (регистрация, вход, профиль)
- ✅ JWT токенами с bcrypt хешированием паролей
- ✅ Интеграцией с WhatsApp Cloud API
- ✅ Хранением сообщений и контактов
- ✅ Современным UI на React с Tailwind CSS
- ✅ Type-safe кодом (TypeScript, Pydantic)

---

## 📁 Структура проекта

```
no-lose/
├── backend/                           # FastAPI приложение
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # Точка входа, конфиг FastAPI
│   │   │
│   │   ├── core/
│   │   │   ├── config.py             # Конфигурация (DB, JWT, WhatsApp)
│   │   │   ├── auth.py               # JWT логика, password hashing
│   │   │   └── database.py           # Подключение PostgreSQL
│   │   │
│   │   ├── models/
│   │   │   ├── user.py               # User модель (email, пароль, профиль)
│   │   │   └── whatsapp.py           # Contact, Message, Conversation модели
│   │   │
│   │   ├── api/
│   │   │   ├── auth.py               # Endpoints: register, login, profile
│   │   │   └── routes.py             # Endpoints: messages, contacts, stats
│   │   │
│   │   └── services/
│   │       └── whatsapp.py           # WhatsApp Cloud API сервис
│   │
│   ├── requirements.txt               # Python зависимости
│   └── venv/                          # Virtual environment
│
├── frontend/                          # Next.js приложение
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Главная страница (Home)
│   │   │   ├── layout.tsx            # Root layout с AuthProvider
│   │   │   ├── globals.css           # Глобальные Tailwind стили
│   │   │   │
│   │   │   ├── login/
│   │   │   │   └── page.tsx          # Страница входа
│   │   │   │
│   │   │   ├── register/
│   │   │   │   └── page.tsx          # Страница регистрации
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx          # Персональный кабинет
│   │   │   │
│   │   │   └── account/
│   │   │       └── page.tsx          # Настройки профиля
│   │   │
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx       # React Context для аутентификации
│   │   │
│   │   └── lib/
│   │       └── api.ts                # API клиент для backend
│   │
│   ├── package.json                  # npm зависимости
│   ├── tsconfig.json                 # TypeScript конфигурация
│   ├── tailwind.config.ts            # Tailwind конфигурация
│   └── node_modules/                 # npm пакеты
│
└── README.md                          # Эта документация
```

---

## 💻 Технологический стек

### Backend
| Компонент | Технология | Версия | Назначение |
|-----------|-----------|--------|-----------|
| Фреймворк | FastAPI | 0.109.0 | Web API |
| Сервер | Uvicorn | 0.27.0 | ASGI сервер |
| БД | PostgreSQL | 15+ | Хранилище данных |
| ORM | SQLAlchemy | 2.0.25 | Работа с БД |
| Драйвер БД | Psycopg | 3.1.0+ | PostgreSQL драйвер |
| Валидация | Pydantic | 2.5.3 | Валидация данных |
| JWT | Python-Jose | 3.3.0 | JWT токены |
| Хеширование | Bcrypt | 4.0.0+ | Хеширование паролей |
| HTTP клиент | HTTPX | 0.26.0 | Async HTTP запросы |
| Миграции | Alembic | 1.13.1 | Версионирование БД |

### Frontend
| Компонент | Технология | Версия | Назначение |
|-----------|-----------|--------|-----------|
| Фреймворк | Next.js | 16.1.3 | React фреймворк |
| Библиотека | React | 19.2.3 | UI компоненты |
| Язык | TypeScript | 5.0+ | Типизированный JS |
| Стили | Tailwind CSS | 4.0+ | Utility CSS |
| Линтинг | ESLint | 9.0+ | Code quality |

### Внешние сервисы
- **Meta WhatsApp Cloud API** - интеграция с WhatsApp
- **PostgreSQL** - реляционная БД

---

## 🚀 Установка и запуск

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+

### Инициализация БД

```bash
# Создать БД и пользователя в PostgreSQL
psql -U postgres
```

```sql
CREATE USER wa_user WITH PASSWORD 'wa_password';
CREATE DATABASE wa_database OWNER wa_user;
GRANT ALL PRIVILEGES ON DATABASE wa_database TO wa_user;
```

### Backend

```bash
cd backend

# Создать virtual environment
python -m venv venv

# Активировать venv
source venv/bin/activate  # macOS/Linux
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер (с hot reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Результат:**
- API доступен на `http://localhost:8000`
- Swagger UI docs: `http://localhost:8000/docs`
- ReDoc docs: `http://localhost:8000/redoc`

### Frontend

```bash
cd frontend

# Установить зависимости
npm install

# Запустить dev сервер (с hot reload)
npm run dev
```

**Результат:**
- Приложение доступно на `http://localhost:3000`

### .env файлы

#### `backend/.env` (создать если нет)
```env
# Database
DATABASE_URL=postgresql+psycopg://wa_user:wa_password@localhost:5432/wa_database

# JWT
SECRET_KEY=your-secret-key-change-in-production-use-strong-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# WhatsApp API
WA_PHONE_NUMBER_ID=your_phone_number_id_here
WA_BUSINESS_ACCOUNT_ID=your_business_account_id_here
WA_ACCESS_TOKEN=your_access_token_here
WA_VERIFY_TOKEN=my_verify_token_change_this
WA_APP_SECRET=your_app_secret_here
WA_API_BASE_URL=https://graph.facebook.com/v18.0
```

#### `frontend/.env.local` (если нужно)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🏗️ Архитектура

### Backend архитектура

```
HTTP Request
    ↓
FastAPI Router
    ↓
Dependency Injection (get_db, get_current_user)
    ↓
Handler (endpoint функция)
    ↓
SQLAlchemy ORM
    ↓
PostgreSQL Database
```

### Frontend архитектура

```
User Action
    ↓
React Component
    ↓
API Client (lib/api.ts)
    ↓
HTTP Request to Backend
    ↓
AuthContext (Context API)
    ↓
localStorage (token persistence)
    ↓
Component Re-render
```

---

## 📡 API документация

### Базовый URL
```
http://localhost:8000/api
```

### Authentication Endpoints (`/auth`)

#### 📝 POST `/auth/register`
**Регистрация нового пользователя**

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "name": "John Doe"
  }'
```

**Запрос:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Ответ (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true,
  "created_at": "2025-01-24T10:30:00"
}
```

**Ошибки:**
- 400: Email уже зарегистрирован
- 422: Невалидные данные

---

#### 🔑 POST `/auth/login`
**Вход пользователя, получение JWT токена**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

**Запрос:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Ответ (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Ошибки:**
- 401: Неправильный email или пароль
- 422: Невалидные данные

---

#### 👤 GET `/auth/me`
**Получить профиль текущего пользователя**

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGc..."
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Ответ (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true,
  "created_at": "2025-01-24T10:30:00"
}
```

**Ошибки:**
- 401: Некорректный или истекший токен

---

#### ✏️ PUT `/auth/me`
**Обновить профиль пользователя**

```bash
curl -X PUT "http://localhost:8000/api/auth/me?name=Jane%20Doe" \
  -H "Authorization: Bearer eyJhbGc..."
```

**Query параметры:**
- `name` (string): Новое имя пользователя

**Headers:**
```
Authorization: Bearer {access_token}
```

**Ответ (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "Jane Doe",
  "is_active": true,
  "created_at": "2025-01-24T10:30:00"
}
```

**Ошибки:**
- 401: Некорректный токен
- 422: Невалидные параметры

---

### Data Endpoints

#### 💚 GET `/health`
**Проверка здоровья API**

```bash
curl http://localhost:8000/api/health
```

**Ответ (200):**
```json
{
  "status": "ok"
}
```

---

#### 📊 GET `/stats`
**Получить статистику сообщений и контактов**

```bash
curl http://localhost:8000/api/stats
```

**Ответ (200):**
```json
{
  "total_messages": 150,
  "total_contacts": 45,
  "total_conversations": 30,
  "inbound_messages": 95,
  "outbound_messages": 55
}
```

---

#### 💬 GET `/messages`
**Получить сообщения (пагинированный список)**

```bash
curl "http://localhost:8000/api/messages?skip=0&limit=50&contact_id=5"
```

**Query параметры:**
- `skip` (int, default=0): Количество пропускаемых записей
- `limit` (int, default=100): Максимум записей на страницу
- `contact_id` (int, optional): Фильтр по ID контакта

**Ответ (200):**
```json
{
  "messages": [
    {
      "id": 1,
      "wa_message_id": "wamid.xxx",
      "contact_id": 5,
      "type": "text",
      "content": "Hello!",
      "is_outbound": false,
      "status": "received",
      "timestamp": "2025-01-24T10:30:00"
    },
    {
      "id": 2,
      "wa_message_id": "wamid.yyy",
      "contact_id": 5,
      "type": "text",
      "content": "Hi there!",
      "is_outbound": true,
      "status": "delivered",
      "timestamp": "2025-01-24T10:31:00"
    }
  ]
}
```

---

#### 👥 GET `/contacts`
**Получить все контакты (пагинированный список)**

```bash
curl "http://localhost:8000/api/contacts?skip=0&limit=50"
```

**Query параметры:**
- `skip` (int, default=0): Смещение
- `limit` (int, default=100): Максимум записей

**Ответ (200):**
```json
{
  "contacts": [
    {
      "id": 5,
      "wa_id": "37125551234",
      "name": "John Smith",
      "profile_name": "john_smith",
      "created_at": "2025-01-20T15:30:00"
    }
  ]
}
```

---

#### 🗨️ GET `/conversations`
**Получить все разговоры (пагинированный список)**

```bash
curl "http://localhost:8000/api/conversations?skip=0&limit=50"
```

**Query параметры:**
- `skip` (int, default=0): Смещение
- `limit` (int, default=100): Максимум записей

**Ответ (200):**
```json
{
  "conversations": [
    {
      "id": 3,
      "contact_id": 5,
      "started_at": "2025-01-20T15:30:00",
      "last_message_at": "2025-01-24T10:31:00",
      "is_active": true
    }
  ]
}
```

---

### WhatsApp Endpoints (`/whatsapp`)

#### ✅ GET `/whatsapp/verify`
**Проверить access token и подключение к WhatsApp API**

```bash
curl http://localhost:8000/api/whatsapp/verify
```

**Ответ (200):**
```json
{
  "status": "ok",
  "data": {
    "id": "123456789"
  }
}
```

---

#### 🏢 GET `/whatsapp/profile`
**Получить информацию о бизнес-профиле**

```bash
curl http://localhost:8000/api/whatsapp/profile
```

**Ответ (200):**
```json
{
  "about": "Welcome to our business!",
  "address": "123 Main St, City",
  "description": "We sell products online",
  "email": "business@example.com",
  "profile_picture_url": "https://...",
  "websites": ["https://example.com"],
  "vertical": "RETAIL"
}
```

---

#### 📱 GET `/whatsapp/phone-numbers`
**Получить все номера телефонов компании**

```bash
curl http://localhost:8000/api/whatsapp/phone-numbers
```

**Ответ (200):**
```json
[
  {
    "id": "phone_number_id_1",
    "display_phone_number": "+1-555-012-3456",
    "quality_rating": "GREEN",
    "status": "CONNECTED"
  }
]
```

---

#### 📋 GET `/whatsapp/templates`
**Получить сохранённые шаблоны сообщений**

```bash
curl http://localhost:8000/api/whatsapp/templates
```

**Ответ (200):**
```json
{
  "data": [
    {
      "id": "template_id_1",
      "name": "hello_world",
      "status": "APPROVED",
      "category": "MARKETING"
    }
  ]
}
```

---

### Webhook Endpoints

#### 🔔 GET `/webhook`
**Verify webhook (Facebook требует при установке)**

```bash
curl "http://localhost:8000/api/webhook?hub.mode=subscribe&hub.verify_token=my_verify_token&hub.challenge=1158201444"
```

**Query параметры:**
- `hub.mode`: "subscribe"
- `hub.verify_token`: Должен совпадать с `WA_VERIFY_TOKEN`
- `hub.challenge`: Число, которое нужно вернуть

**Ответ (200):**
```
1158201444
```

---

#### 📨 POST `/webhook`
**Receive incoming messages from WhatsApp**

Автоматически вызывается Facebook при новых сообщениях.

**Примерный payload от Facebook:**
```json
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "id": "wamid.xxx",
          "from": "37125551234",
          "type": "text",
          "text": {
            "body": "Hello!"
          },
          "timestamp": "1234567890"
        }],
        "contacts": [{
          "profile": {
            "name": "John Smith"
          },
          "wa_id": "37125551234"
        }]
      }
    }]
  }]
}
```

**Ответ (200):**
```json
{
  "status": "ok",
  "message_id": 42
}
```

---

## 🎨 Frontend страницы

### 🏠 Home (`/`)
**Главная страница приложения**

**Что там есть:**
- Header с логотипом "No Lose"
- Navigation с кнопками Login и Register
- Hero section: "Hello World"
- Описание платформы
- CTA кнопки: "Get Started" и "Sign In"
- Footer с копирайтом

**Дизайн:**
- Gradient фон: синий-индиго (blue-50 to indigo-100)
- Поддержка темного режима
- Responsive: работает на мобильных

**Доступна всем:** ✅ Не требует аутентификации

---

### 🔐 Login (`/login`)
**Страница входа в аккаунт**

**Форма содержит:**
- Email поле
- Password поле (type="password")
- Submit кнопка ("Sign in" / "Signing in...")
- Error сообщение (если неправильный email/пароль)
- Link на регистрацию ("Don't have an account? Register")

**Функциональность:**
```
1. Пользователь заполняет форму
2. На submit: валидация полей
3. API запрос: POST /auth/login
4. Если успех:
   - Сохранение токена в localStorage
   - Обновление AuthContext
   - Редирект на /dashboard
5. Если ошибка:
   - Показ error сообщения
```

**Дизайн:**
- Форма по центру (max-width: 28rem)
- Белая карточка (dark: серая)
- Tailwind CSS стили

**Доступна всем:** ✅ Не требует аутентификации

---

### 📝 Register (`/register`)
**Страница регистрации нового аккаунта**

**Форма содержит:**
- Name поле
- Email поле
- Password поле (type="password")
- Confirm Password поле (type="password")
- Submit кнопка ("Create account" / "Creating account...")
- Error сообщение (если ошибка)
- Link на вход ("Already have an account? Sign in")

**Функциональность:**
```
1. Пользователь заполняет форму
2. На submit: валидация
   - Пароли совпадают?
   - Пароль >= 6 символов?
3. API запрос: POST /auth/register
4. Если успех:
   - Автоматический login (POST /auth/login)
   - Сохранение токена
   - Обновление AuthContext
   - Редирект на /dashboard
5. Если ошибка:
   - Показ error сообщения
```

**Дизайн:**
- Форма по центру (max-width: 28rem)
- Белая карточка
- Tailwind CSS

**Доступна всем:** ✅ Не требует аутентификации

---

### 📊 Dashboard (`/dashboard`)
**Персональный кабинет пользователя**

**Структура страницы:**
```
┌─────────────────────────────────────┐
│ Navigation Bar                      │
│ Logo  |  Account  |  Logout         │
├─────────────────────────────────────┤
│                                     │
│  Hello, John Doe!                   │
│                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────┐│
│  │  Stats   │ │ Activity │ │ News ││
│  └──────────┘ └──────────┘ └──────┘│
│                                     │
└─────────────────────────────────────┘
```

**Компоненты:**
1. **Navigation Bar**
   - Logo "No Lose"
   - Link на Account (/account)
   - Button Logout

2. **Hero Card**
   - "Hello, {user.name}!"
   - Приветственное сообщение

3. **Stats Card**
   - Статистика

4. **Recent Activity Card**
   - Последние действия

5. **Notifications Card**
   - Уведомления

**Функциональность:**
```
1. При загрузке:
   - Проверка AuthContext
   - Если не аутентифицирован:
     - Если loading -> spinner
     - Если no user -> редирект на /login
   - Если аутентифицирован:
     - Загрузка данных с backend
     - Отрисовка страницы

2. На Logout:
   - Очистка токена из localStorage
   - Обновление AuthContext
   - Редирект на /
```

**Защита:** 🔒 Требует аутентификации (редирект на /login если нет)

---

### ⚙️ Account (`/account`)
**Настройки профиля пользователя**

**Структура страницы:**
```
┌─────────────────────────────────────┐
│ Navigation Bar                      │
│ Logo  |  Dashboard  |  Logout       │
├─────────────────────────────────────┤
│                                     │
│  Account Settings                   │
│                                     │
│  Email: john@example.com (disabled) │
│  Name:  [John Doe       ]           │
│  Since: Jan 20, 2025                │
│                                     │
│  [✓] Save Changes                   │
│                                     │
│  Success/Error message              │
│                                     │
└─────────────────────────────────────┘
```

**Компоненты:**
1. **Navigation Bar**
   - Logo
   - Link на Dashboard
   - Logout button

2. **Profile Card**
   - Email (disabled, read-only)
   - Name (editable текстовое поле)
   - "Member since" дата
   - Save Changes кнопка

3. **Message**
   - Успешно сохранено / Ошибка

**Функциональность:**
```
1. При загрузке:
   - Проверка AuthContext
   - Если не аутентифицирован -> редирект на /login
   - Заполнение полей из user объекта

2. На Save:
   - Валидация name поля
   - API запрос: PUT /auth/me?name={name}
   - Если успех:
     - Показ "Profile updated!"
     - Обновление user в context
   - Если ошибка:
     - Показ error сообщения

3. На Logout:
   - Очистка токена
   - Редирект на /
```

**Защита:** 🔒 Требует аутентификации

---

## 📦 Database схема

### Таблица: `users`

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  hashed_password VARCHAR(255) NOT NULL,
  name VARCHAR(100) NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**Примерная запись:**
```json
{
  "id": 1,
  "email": "john@example.com",
  "hashed_password": "$2b$12$...",
  "name": "John Doe",
  "is_active": true,
  "created_at": "2025-01-24T10:30:00",
  "updated_at": "2025-01-24T10:30:00"
}
```

---

### Таблица: `contacts`

```sql
CREATE TABLE contacts (
  id SERIAL PRIMARY KEY,
  wa_id VARCHAR(50) NOT NULL UNIQUE,
  name VARCHAR(255),
  profile_name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_contacts_wa_id ON contacts(wa_id);
```

---

### Таблица: `conversations`

```sql
CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  contact_id INTEGER NOT NULL REFERENCES contacts(id),
  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_message_at TIMESTAMP,
  is_active BOOLEAN DEFAULT true,

  FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversations_contact_id ON conversations(contact_id);
```

---

### Таблица: `messages`

```sql
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,

  -- IDs
  wa_message_id VARCHAR(255) NOT NULL UNIQUE,
  contact_id INTEGER NOT NULL REFERENCES contacts(id),
  conversation_id INTEGER NOT NULL REFERENCES conversations(id),

  -- Содержимое
  message_type VARCHAR(50) NOT NULL,      -- text, image, video, audio, document
  content TEXT,
  media_url VARCHAR(500),
  media_id VARCHAR(255),

  -- Направление
  is_outbound BOOLEAN NOT NULL,
  status VARCHAR(50) DEFAULT 'received',  -- sent, delivered, read, failed

  -- Времена
  timestamp TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  -- Отладка
  raw_data JSONB,

  FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_contact_id ON messages(contact_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
```

---

## 🔐 Аутентификация

### JWT Flow

```
┌─────────────────────────────────────────────────┐
│ User Registration / Login                       │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. POST /auth/register или POST /auth/login    │
│    - Email, Password отправляется              │
│                                                 │
│ 2. Backend проверяет:                           │
│    - Email существует (для login)               │
│    - Пароль верный (bcrypt verify)              │
│                                                 │
│ 3. Backend создаёт JWT токен:                   │
│    - Header: { alg: "HS256", typ: "JWT" }      │
│    - Payload: { sub: email, exp: time }        │
│    - Signature: HMAC-SHA256(header.payload)     │
│                                                 │
│ 4. Backend возвращает токен в ответе           │
│    { access_token: "eyJ...", token_type: "bearer" }
│                                                 │
│ 5. Frontend сохраняет:                          │
│    - localStorage (persistence)                │
│    - AuthContext (для компонентов)            │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Защита endpoint-ов

```
┌─────────────────────────────────────────────────┐
│ Protected Endpoint Request                       │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Frontend отправляет запрос:                   │
│    Header: "Authorization: Bearer eyJ..."       │
│                                                 │
│ 2. FastAPI middleware:                          │
│    - Извлекает токен из header                 │
│    - Вызывает get_current_user() dependency    │
│                                                 │
│ 3. get_current_user():                          │
│    - Декодирует JWT с secret_key               │
│    - Извлекает email из payload                │
│    - Находит User в БД                         │
│    - Если ошибка -> 401 Unauthorized           │
│                                                 │
│ 4. Endpoint получает User объект                │
│    - Может использовать user.id, user.email    │
│                                                 │
│ 5. Возвращает ответ                             │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Password Security

```python
# Регистрация (хеширование)
plain_password = "MySecure123!"
hashed = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt())
# Сохраняется в БД: $2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcg7b3XeKeUxWdeS...

# Вход (проверка)
plain_password = "MySecure123!"
is_valid = bcrypt.checkpw(plain_password.encode(), stored_hash.encode())
# True или False
```

---

## 🔄 Основные потоки

### Поток регистрации

```
Frontend                          Backend
   │                               │
   ├──── POST /auth/register ─────>│
   │      {email, password, name}  │
   │                               │
   │                        Check email uniqueness
   │                        Hash password with bcrypt
   │                        Save User to DB
   │                               │
   │<──── 200 User object ─────────┤
   │                               │
   ├──── POST /auth/login ─────────>│
   │      {email, password}         │
   │                               │
   │                        Verify password
   │                        Create JWT token (30 min)
   │                               │
   │<──── Token response ───────────┤
   │                               │
   Save to localStorage
   Save to AuthContext
   Redirect to /dashboard
```

### Поток входа

```
Frontend                          Backend
   │                               │
   ├──── POST /auth/login ────────>│
   │      {email, password}        │
   │                               │
   │                        Find user by email
   │                        Verify password
   │                        If valid:
   │                          Create JWT token
   │                        If invalid:
   │                          Return 401 error
   │                               │
   │<──── Token or Error ──────────┤
   │                               │
   If success:
     Save token to localStorage
     Update AuthContext
     Redirect to /dashboard
   If error:
     Show error message
```

### Поток доступа к защищённым страницам

```
Frontend                          Backend
   │
   User navigates to /dashboard
   │
   Check AuthContext.user
   │
   If loading:
     Show spinner
   │
   If !user && !loading:
     Redirect to /login
   │
   If user:
     Render dashboard
     │
     ├──── GET /auth/me ──────────>│
     │      Header: Auth Bearer    │
     │                              │
     │                      Decode JWT
     │                      Find user in DB
     │                               │
     │<──── User object ────────────┤
     │                               │
     Update context, render page
```

### Поток получения данных

```
Frontend                          Backend
   │
   useEffect(() => {
     loadData()
   }, [])
   │
   ├──── GET /api/messages ──────>│
   │      or /api/contacts          │
   │      or /api/stats             │
   │                                │
   │                        Query database
   │                        Return data
   │                                │
   │<──── Data array ──────────────┤
   │                                │
   setState(data)
   Render component with data
```

### WhatsApp Webhook Flow

```
Facebook                          Backend                        DB
   │                               │                            │
   ├──── POST /api/webhook ──────>│                            │
   │      {message, contact info}  │                            │
   │                               │                            │
   │                        Parse message
   │                        Extract contact wa_id
   │                        Extract message content
   │                               │                            │
   │                               ├─ Find/Create Contact ────>│
   │                               │                            │
   │                               ├─ Find/Create Conversation>│
   │                               │                            │
   │                               ├─ Create Message ─────────>│
   │                               │                            │
   │<──── 200 { status: "ok" } ───┤                            │
   │                               │                            │
   (Message stored in DB,
    visible in /api/messages)
```

---

## 🛠️ Разработка

### Часто используемые команды

#### Backend
```bash
# Запуск dev сервера
uvicorn app.main:app --reload

# Запуск с определённым портом
uvicorn app.main:app --reload --port 8001

# Создать миграцию (Alembic)
alembic revision --autogenerate -m "Add new column"

# Применить миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1
```

#### Frontend
```bash
# Запуск dev сервера
npm run dev

# Построить для production
npm run build

# Запустить production версию
npm start

# Lint код
npm run lint

# Форматировать код
npm run format
```

---

## 🐛 Troubleshooting

### Backend ошибки

**"Could not connect to database"**
- ✅ Проверить, что PostgreSQL запущен
- ✅ Проверить DATABASE_URL в .env
- ✅ Проверить, что пользователь wa_user существует и имеет доступ

**"ModuleNotFoundError: No module named 'app'"**
- ✅ Убедитесь, что в `backend/` каталоге
- ✅ Виртуальное окружение активировано
- ✅ `pip install -r requirements.txt` выполнен

**"401 Unauthorized" при запросе к защищённому endpoint**
- ✅ Проверить, что токен отправляется в header
- ✅ Проверить, что формат: `Authorization: Bearer {token}`
- ✅ Проверить, что токен не истёк (30 минут)

### Frontend ошибки

**"Cannot POST http://localhost:8000/api/auth/login"**
- ✅ Убедитесь, что backend сервер запущен
- ✅ Проверьте CORS в `backend/app/main.py`
- ✅ Проверьте, что http://localhost:3000 в allow_origins

**"AuthProvider not found"**
- ✅ Проверьте, что `<AuthProvider>` обёрнут вокруг children в layout.tsx

**"localStorage is not defined"**
- ✅ Убедитесь, что код в клиентском компоненте (используйте "use client")
- ✅ В контексте используйте useEffect для инициализации

---

## 📚 Дополнительные ресурсы

### Документация
- [FastAPI документация](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Next.js документация](https://nextjs.org/docs)
- [React документация](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Meta WhatsApp API](https://developers.facebook.com/docs/whatsapp/cloud-api/)

### Полезные инструменты
- **Postman** или **Insomnia** - тестирование API
- **pgAdmin** или **DBeaver** - управление PostgreSQL
- **JWT Debugger** - проверка JWT токенов

---

## 📝 Лицензия

Этот проект является приватным SaaS проектом.

---

**Последнее обновление:** 24 января 2025 года

Для вопросов или предложений - добавляйте issues в git репозиторий.
