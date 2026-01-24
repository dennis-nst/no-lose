# WhatsApp Data Collector - Setup Guide

## Структура проекта

```
WA app/
├── backend/           # FastAPI бэкенд
│   ├── app/
│   │   ├── api/       # API endpoints
│   │   ├── core/      # Конфигурация и база данных
│   │   ├── models/    # SQLAlchemy модели
│   │   └── services/  # WhatsApp сервис
│   ├── .env           # Переменные окружения
│   └── requirements.txt
├── frontend/          # Next.js фронтенд
├── docker-compose.yml # PostgreSQL в Docker
└── SETUP.md
```

## Шаг 1: Запуск PostgreSQL

```bash
docker-compose up -d
```

Это запустит PostgreSQL на порту 5432 с:
- User: `wa_user`
- Password: `wa_password`
- Database: `wa_database`

## Шаг 2: Настройка бэкенда

```bash
cd backend

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен на http://localhost:8000
Документация: http://localhost:8000/docs

## Шаг 3: Запуск фронтенда

```bash
cd frontend
npm run dev
```

Фронтенд будет доступен на http://localhost:3000

---

## Настройка WhatsApp Cloud API

### 1. Создание Meta Business Account

1. Перейдите на https://business.facebook.com
2. Создайте бизнес-аккаунт (если ещё нет)
3. Подтвердите бизнес (верификация)

### 2. Создание приложения в Meta for Developers

1. Перейдите на https://developers.facebook.com
2. Нажмите "My Apps" → "Create App"
3. Выберите тип "Business"
4. Заполните название приложения
5. В Dashboard найдите "WhatsApp" и нажмите "Set Up"

### 3. Настройка WhatsApp Business API

1. В разделе WhatsApp → Getting Started:
   - Вы получите **Test Phone Number** для тестирования
   - Добавьте номера для тестирования (до 5 номеров бесплатно)

2. Запишите важные данные:
   - **Phone Number ID** - ID тестового номера
   - **WhatsApp Business Account ID** - ID бизнес-аккаунта
   - **Temporary Access Token** - временный токен (действует 24 часа)

### 4. Coexistence Mode (важно!)

Coexistence позволяет использовать Cloud API параллельно с WhatsApp Business App:

1. Перейдите в WhatsApp → API Setup
2. В разделе "Phone numbers" выберите номер
3. Если номер уже привязан к WhatsApp Business App:
   - Meta автоматически включит Coexistence
   - Вы сможете получать сообщения через API webhook
   - При этом WhatsApp Business App продолжит работать

**Ограничения Coexistence:**
- Только входящие сообщения через webhook
- Отправка сообщений - через API или приложение (не одновременно)
- История сообщений не синхронизируется между API и приложением

### 5. Настройка Webhook

Для получения сообщений нужен публичный URL. Варианты:

**Вариант A: ngrok (для тестирования)**
```bash
ngrok http 8000
```
Получите URL вида `https://xxxx.ngrok.io`

**Вариант B: Публичный сервер**
Разверните приложение на сервере с HTTPS

**Настройка в Meta:**
1. WhatsApp → Configuration → Webhook
2. Callback URL: `https://your-domain.com/api/webhook`
3. Verify Token: `my_verify_token` (или ваш токен из .env)
4. Подписаться на: `messages`

### 6. Обновление .env

Отредактируйте `backend/.env`:

```env
DATABASE_URL=postgresql://wa_user:wa_password@localhost:5432/wa_database

WA_PHONE_NUMBER_ID=123456789012345
WA_BUSINESS_ACCOUNT_ID=123456789012345
WA_ACCESS_TOKEN=EAAG...your_token
WA_VERIFY_TOKEN=my_verify_token
WA_APP_SECRET=your_app_secret
```

### 7. Получение постоянного токена

Временный токен действует 24 часа. Для постоянного:

1. System User:
   - Business Settings → Users → System Users
   - Создайте System User с правами Admin
   - Назначьте доступ к WhatsApp Business Account
   - Generate Token с permissions: `whatsapp_business_messaging`, `whatsapp_business_management`

---

## Проверка работы

### 1. Проверка API

```bash
curl http://localhost:8000/api/health
```

### 2. Проверка подключения к WhatsApp

```bash
curl http://localhost:8000/api/whatsapp/verify
```

### 3. Получение профиля бизнеса

```bash
curl http://localhost:8000/api/whatsapp/profile
```

### 4. Тестирование webhook

Отправьте сообщение на тестовый номер WhatsApp.
Оно должно появиться в базе данных и на фронтенде.

---

## API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/health` | Проверка работы API |
| GET | `/api/whatsapp/verify` | Проверка токена WA |
| GET | `/api/whatsapp/profile` | Профиль бизнеса |
| GET | `/api/whatsapp/phone-numbers` | Список номеров |
| GET | `/api/whatsapp/templates` | Шаблоны сообщений |
| GET | `/api/webhook` | Верификация webhook |
| POST | `/api/webhook` | Получение сообщений |
| GET | `/api/messages` | Список сообщений |
| GET | `/api/contacts` | Список контактов |
| GET | `/api/conversations` | Список разговоров |
| GET | `/api/stats` | Статистика |

---

## Troubleshooting

**Ошибка подключения к БД:**
- Проверьте что Docker запущен: `docker ps`
- Проверьте логи: `docker-compose logs postgres`

**Ошибка 401 от WhatsApp API:**
- Проверьте Access Token (возможно истёк)
- Сгенерируйте новый токен

**Webhook не получает сообщения:**
- Проверьте что URL публично доступен
- Проверьте что подписка на `messages` активна
- Проверьте логи бэкенда

**CORS ошибки:**
- Фронтенд должен работать на http://localhost:3000
