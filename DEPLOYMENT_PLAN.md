# GCP Production Deployment Plan для No Lose SaaS

## Executive Summary

Этот план подготавливает No Lose SaaS к production deployment в Google Cloud Platform с полной интеграцией Evolution API для WhatsApp и автоматизированным CI/CD через GitHub Actions.

**Ключевые решения:**
- ✅ Evolution API для скачивания истории чатов WhatsApp
- ✅ VM e2-micro + Docker (бесплатный tier GCP)
- ✅ GitHub Actions для автоматического deployment
- ✅ .env файлы на сервере для секретов
- ✅ PostgreSQL на VM (не Cloud SQL для экономии)

**Общее время выполнения:** 6-8 часов

**Параметры sync:**
- История чатов: последние 30 сообщений per chat
- Архивация: сообщения старше 2 лет

---

## Статус выполнения

### ✅ Выполнено (Claude):
1. ✅ Backend интеграция Evolution API (создание моделей, сервисов, API endpoints)
2. ✅ Frontend страницы для WhatsApp подключения и sync
3. ✅ Database migrations
4. ✅ GitHub Actions workflow
5. ✅ GCP VM создан и настроен (e2-micro, IP: 34.123.68.109)
6. ✅ Docker + Docker Compose установлены
7. ✅ Приложение развернуто и работает
8. ✅ Исправлена критическая ошибка DATABASE_URL (postgresql+psycopg)

### 🔶 Опционально (User):
1. 🔶 GitHub Secrets для автоматического CI/CD (см. Phase 3.2)
2. 🔶 SSL/HTTPS setup с Let's Encrypt (см. Phase 4.4)
3. 🔶 Полное тестирование функционала (см. Phase 6)

### 🎯 Приложение доступно:
- **URL**: http://34.123.68.109
- **API Health**: http://34.123.68.109/api/health
- **Статус**: Все 5 контейнеров работают

**Следующий шаг после утверждения:** Claude начнет с Phase 1 - Evolution API Backend Integration.

---

## Текущее состояние проекта

### Технологический стек
**Backend:**
- FastAPI 0.109.0 + SQLAlchemy 2.0.25
- PostgreSQL 15
- JWT аутентификация (python-jose + bcrypt)
- httpx для HTTP запросов

**Frontend:**
- Next.js 16.1.3 (App Router)
- React 19.2.3
- Tailwind CSS 4.x
- TypeScript

**Инфраструктура:**
- Docker контейнеризация (все сервисы)
- Nginx reverse proxy
- Оптимизировано для GCP e2-micro (1GB RAM)

### Критическая проблема: WhatsApp API Integration Gap

**Обнаружено несоответствие:**

1. **Backend код** ([backend/app/services/whatsapp.py](../../../Cursor/no-lose/backend/app/services/whatsapp.py)) использует WhatsApp Cloud API (Meta)
2. **Production конфиг** ([docker-compose.prod.yml](../../../Cursor/no-lose/docker-compose.prod.yml)) запускает Evolution API контейнер
3. **Backend НЕ интегрирован** с Evolution API - контейнер работает, но код не использует

**Решение:** Полная интеграция Evolution API в backend с сохранением текущего WhatsApp Cloud API кода (dual API strategy).

---

## Архитектурные решения

### 1. Dual API Strategy для WhatsApp

**Решение:** Использовать оба API одновременно

| API | Использование |
|-----|--------------|
| **Evolution API** | QR-код подключение, скачивание истории чатов, получение новых сообщений |
| **WhatsApp Cloud API** | Отправка template сообщений (опционально для бизнес-функций) |

**Преимущества:**
- Evolution API: доступ к истории существующих чатов
- QR-код авторизация без бизнес-верификации
- Fallback на официальный API при необходимости

### 2. GCP Infrastructure: VM e2-micro + Docker

**Выбрано:** VM e2-micro (бесплатный tier)

**Конфигурация:**
- Machine type: e2-micro (1 vCPU, 1GB RAM)
- Disk: 30GB pd-standard
- OS: Ubuntu 22.04 LTS
- Zone: us-west1-b (free tier eligible)
- Swap: 2GB для компенсации ограниченной RAM

**Стоимость:** $0/месяц (бесплатный tier GCP)

### 3. CI/CD: GitHub Actions

**Автоматизация deployment:**
- Trigger: push в `main` branch
- Build Docker images
- SSH deployment на GCP VM
- Zero-downtime restart (docker-compose pull + up)

### 4. Secrets Management: .env файлы

**Решение:** .env файлы на сервере (простое решение для MVP)

**Расположение:**
- Production: `/home/user/no-lose/.env` на VM
- Не коммитим в Git
- Настраиваем вручную при первом deployment

---

## Implementation Phases

**Обозначения:** 👤 User | 🤖 Claude

### Phase 1: Evolution API Backend Integration (3 hours) 🤖

**Кто выполняет:** Claude автоматически создает все файлы и модификации

Интеграция Evolution API в backend код для работы с историей чатов WhatsApp.

#### 1.1 Update Configuration (15 min)

**Файл:** [backend/app/core/config.py](../../../Cursor/no-lose/backend/app/core/config.py)

Добавить поля:
```python
# Evolution API Settings
evolution_api_url: str = "http://evolution:8080"
evolution_api_key: str = ""
```

**Файл:** [backend/.env.example](../../../Cursor/no-lose/backend/.env.example)

Добавить:
```env
EVOLUTION_API_URL=http://evolution:8080
EVOLUTION_API_KEY=your_secure_key_here
```

#### 1.2 Create Evolution Instance Model (20 min)

**Новый файл:** `backend/app/models/evolution.py`

Модель для отслеживания WhatsApp instances:
- `id`, `user_id` (FK to users)
- `instance_name` (unique, формат: `user_{user_id}`)
- `status` (disconnected/qr/connecting/connected)
- `qr_code` (Base64), `qr_code_updated_at`
- `phone_number`, `profile_name` (после подключения)
- `created_at`, `updated_at`, `last_connected_at`
- `raw_data` (JSON)

#### 1.3 Update WhatsApp Models (10 min)

**Файл:** [backend/app/models/whatsapp.py](../../../Cursor/no-lose/backend/app/models/whatsapp.py)

Добавить поля для поддержки обоих API:
```python
# В Contact:
evolution_remote_jid = Column(String(100), nullable=True, index=True)

# В Message:
evolution_key_id = Column(String(255), nullable=True, unique=True, index=True)
source = Column(String(50), default="cloud_api")  # cloud_api | evolution_api
```

#### 1.4 Create Evolution Service Layer (1.5 hours)

**Новый файл:** `backend/app/services/evolution.py`

Класс `EvolutionAPIService` с методами:

**Instance Management:**
- `create_instance(instance_name)` - POST /instance/create
- `connect_instance(instance_name)` - POST /instance/connect/{name}
- `get_instance_status(instance_name)` - GET /instance/connectionState/{name}
- `get_instance_qrcode(instance_name)` - GET /instance/qrcode/{name}
- `logout_instance(instance_name)` - DELETE /instance/logout/{name}
- `delete_instance(instance_name)` - DELETE /instance/delete/{name}

**Data Fetching:**
- `fetch_contacts(instance_name)` - GET /chat/findContacts/{name}
- `fetch_chats(instance_name)` - GET /chat/findChats/{name}
- `fetch_messages(instance_name, remote_jid, limit=30)` - POST /chat/fetchMessages/{name} (default: 30 последних сообщений)

**Sending:**
- `send_text_message(instance_name, number, text)` - POST /message/sendText/{name}

**Database Sync:**
- `sync_contact_to_db(db, evolution_contact, user_id)` - Contact объект
- `sync_message_to_db(db, evolution_message, user_id)` - Message объект с дедупликацией
- `sync_chat_history(db, instance_name, remote_jid, user_id)` - количество синхронизированных

#### 1.5 Create Evolution API Routes (45 min)

**Новый файл:** `backend/app/api/evolution.py`

Endpoints:
```
POST   /api/evolution/instance/create      - Создать instance + получить QR код
GET    /api/evolution/instance/status      - Статус подключения
DELETE /api/evolution/instance/disconnect  - Отключить WhatsApp
GET    /api/evolution/instance/qrcode      - Обновить QR код

POST   /api/evolution/sync/contacts        - Синхронизировать контакты
POST   /api/evolution/sync/chats           - Получить список чатов
POST   /api/evolution/sync/messages/{contact_id} - Скачать историю чата

POST   /api/evolution/send/text            - Отправить текстовое сообщение
```

Все endpoints требуют `current_user` (JWT auth).

#### 1.6 Add Evolution Webhook (30 min)

**Файл:** [backend/app/api/routes.py](../../../Cursor/no-lose/backend/app/api/routes.py)

Добавить endpoint:
```python
@router.post("/webhook/evolution")
async def evolution_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook для Evolution API событий:
    - messages.upsert: новое сообщение
    - connection.update: изменение статуса подключения
    - qrcode.updated: обновление QR кода
    """
```

#### 1.7 Register Router in Main App (5 min)

**Файл:** [backend/app/main.py](../../../Cursor/no-lose/backend/app/main.py)

```python
from app.api.evolution import router as evolution_router
app.include_router(evolution_router, prefix="/api")
```

---

### Phase 2: Frontend Evolution Integration (2 hours) 🤖

**Кто выполняет:** Claude автоматически создает страницы и компоненты

#### 2.1 Update API Client (20 min)

**Файл:** [frontend/src/lib/api.ts](../../../Cursor/no-lose/frontend/src/lib/api.ts)

Добавить Evolution API методы:
```typescript
export const evolutionApi = {
  createInstance: () => fetch('/api/evolution/instance/create', ...),
  getStatus: () => fetch('/api/evolution/instance/status', ...),
  disconnect: () => fetch('/api/evolution/instance/disconnect', ...),
  getQRCode: () => fetch('/api/evolution/instance/qrcode', ...),

  syncContacts: () => fetch('/api/evolution/sync/contacts', ...),
  syncChats: () => fetch('/api/evolution/sync/chats', ...),
  syncMessages: (contactId: number) => fetch(`/api/evolution/sync/messages/${contactId}`, ...),
}
```

**Исправить hardcoded URL:**
```typescript
// Было:
const API_BASE = 'http://localhost:8000/api'

// Стало:
const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api'
```

#### 2.2 Create WhatsApp Connection Page (1 hour)

**Новый файл:** `frontend/src/app/whatsapp/page.tsx`

Компоненты:
1. **Connection Status Card**
   - Показывает статус (disconnected/connecting/connected)
   - Phone number если connected

2. **QR Code Display**
   - Показывает QR код при status="qr"
   - Auto-refresh каждые 30 секунд
   - Инструкции для сканирования

3. **Action Buttons**
   - "Подключить WhatsApp" - создает instance и показывает QR
   - "Отключить" - logout instance
   - "Обновить QR код"

#### 2.3 Create Chat Sync Page (40 min)

**Новый файл:** `frontend/src/app/whatsapp/sync/page.tsx`

Функции:
1. **Sync Contacts** - кнопка синхронизации всех контактов
2. **Chat List** - список доступных чатов
3. **Message Sync** - кнопка "Скачать историю" для каждого чата
4. **Progress indicators** - показывает процесс синхронизации

---

### Phase 3: GitHub Actions CI/CD Setup (1 hour) 🤖

**Кто выполняет:** Claude создает workflow, User настраивает GitHub Secrets

#### 3.1 Create GitHub Workflow (45 min) 🤖

**Новый файл:** `.github/workflows/deploy.yml`

```yaml
name: Deploy to GCP

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to GCP VM
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.GCP_VM_IP }}
          username: ${{ secrets.GCP_VM_USER }}
          key: ${{ secrets.GCP_SSH_KEY }}
          script: |
            cd /home/${{ secrets.GCP_VM_USER }}/no-lose
            git pull origin main
            docker-compose -f docker-compose.prod.yml pull
            docker-compose -f docker-compose.prod.yml up -d --build
            docker system prune -f
```

#### 3.2 Setup GitHub Secrets (15 min) 👤

**Кто выполняет:** User вручную

В GitHub repo Settings → Secrets → Actions, добавить:
```
GCP_VM_IP=<external-ip-of-vm>
GCP_VM_USER=<username>
GCP_SSH_KEY=<private-ssh-key>
```

SSH ключ генерировать:
```bash
ssh-keygen -t ed25519 -C "github-actions"
# Приватный ключ → GCP_SSH_KEY secret
# Публичный ключ → добавить в VM ~/.ssh/authorized_keys
```

---

### Phase 4: GCP Infrastructure Setup (1.5 hours) 👤

**Кто выполняет:** User выполняет все команды вручную

#### 4.1 Create GCP VM Instance (20 min) 👤

**Использовать существующий скрипт:** [deploy/gcp-setup.sh](../../../Cursor/no-lose/deploy/gcp-setup.sh)

Обновить конфигурацию:
```bash
PROJECT_ID="<your-actual-project-id>"
ZONE="us-west1-b"
INSTANCE_NAME="no-lose-app"
```

Выполнить:
```bash
chmod +x deploy/gcp-setup.sh
./deploy/gcp-setup.sh
```

Получить external IP:
```bash
gcloud compute instances describe no-lose-app \
  --zone=us-west1-b \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

#### 4.2 Initialize VM (30 min)

**SSH в VM:**
```bash
gcloud compute ssh no-lose-app --zone=us-west1-b
```

**Запустить setup скрипт:**
```bash
curl -fsSL https://raw.githubusercontent.com/<your-repo>/main/deploy/server-setup.sh -o setup.sh
chmod +x setup.sh
./setup.sh
```

Это установит:
- Docker + Docker Compose
- Git
- 2GB swap файл

**Logout и login обратно:**
```bash
exit
gcloud compute ssh no-lose-app --zone=us-west1-b
```

#### 4.3 Clone Repository & Configure (20 min)

```bash
git clone https://github.com/<your-username>/no-lose.git
cd no-lose
```

**Создать .env файл:**
```bash
nano .env
```

Добавить production переменные:
```env
# Domain
DOMAIN=<your-domain-or-ip>

# PostgreSQL (используем docker-compose значения)
DATABASE_URL=postgresql://wa_user:wa_password@postgres:5432/wa_database

# JWT
SECRET_KEY=<generate-secure-random-key>
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Evolution API
EVOLUTION_API_URL=http://evolution:8080
EVOLUTION_API_KEY=<generate-secure-key>

# WhatsApp Cloud API (опционально)
WA_PHONE_NUMBER_ID=
WA_BUSINESS_ACCOUNT_ID=
WA_ACCESS_TOKEN=
WA_VERIFY_TOKEN=
WA_APP_SECRET=
```

**Генерация ключей:**
```bash
# SECRET_KEY
openssl rand -hex 32

# EVOLUTION_API_KEY
openssl rand -hex 32
```

#### 4.4 Setup SSL with Let's Encrypt (20 min)

**Установить Certbot:**
```bash
sudo apt install -y certbot
```

**Получить сертификат:**
```bash
# Временно остановить nginx если работает
docker-compose -f docker-compose.prod.yml stop nginx

# Получить сертификат
sudo certbot certonly --standalone \
  -d <your-domain.com> \
  --email <your-email> \
  --agree-tos

# Скопировать сертификаты
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/<your-domain.com>/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/<your-domain.com>/privkey.pem nginx/ssl/
sudo chown -R $USER:$USER nginx/ssl
```

**Обновить nginx.conf для HTTPS:** Добавить server block для port 443 с SSL.

#### 4.5 Initial Deployment (10 min)

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

**Проверить статус:**
```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

**Проверить доступность:** `http://<your-ip-or-domain>`

---

### Phase 5: Database Setup & Migration (30 min) 🤖👤

**Кто выполняет:** Claude создает migrations локально, User запускает на production

#### 5.1 Create Alembic Migration (15 min) 🤖

**На локальной машине (Claude выполняет автоматически):**

```bash
cd backend
source venv/bin/activate

# Создать initial migration
alembic revision --autogenerate -m "Add Evolution API support"

# Проверить generated migration
cat alembic/versions/<timestamp>_add_evolution_api_support.py
```

**Commit migration:**
```bash
git add alembic/versions/
git commit -m "Add database migration for Evolution API"
git push origin main
```

#### 5.2 Run Migration on Production (15 min) 👤

**User выполняет команды вручную:**

**SSH в GCP VM:**
```bash
gcloud compute ssh no-lose-app --zone=us-west1-b
cd no-lose
```

**Exec в backend контейнер:**
```bash
docker-compose -f docker-compose.prod.yml exec backend bash
```

**Внутри контейнера:**
```bash
alembic upgrade head
exit
```

**Проверить таблицы:**
```bash
docker exec -it wa_postgres psql -U wa_user -d wa_database -c "\dt"
```

Должны появиться:
- `evolution_instances` (новая таблица)
- `contacts` с новым полем `evolution_remote_jid`
- `messages` с новыми полями `evolution_key_id`, `source`

---

### Phase 6: Testing & Verification (1 hour) 👤

**Кто выполняет:** User тестирует вручную

#### 6.1 Backend API Tests (20 min) 👤

**Проверить health endpoint:**
```bash
curl https://<your-domain>/api/health
```

**Зарегистрировать тестового пользователя:**
```bash
curl -X POST https://<your-domain>/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","name":"Test User"}'
```

**Login и получить token:**
```bash
curl -X POST https://<your-domain>/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```

**Создать Evolution instance:**
```bash
TOKEN="<jwt-token-from-login>"
curl -X POST https://<your-domain>/api/evolution/instance/create \
  -H "Authorization: Bearer $TOKEN"
```

#### 6.2 Frontend Tests (15 min)

1. Открыть `https://<your-domain>`
2. Зарегистрироваться / войти
3. Перейти на `/whatsapp`
4. Нажать "Подключить WhatsApp"
5. Проверить отображение QR кода
6. Сканировать QR кодом из WhatsApp приложения
7. Проверить статус меняется на "connected"

#### 6.3 Evolution API Integration Test (25 min)

**После подключения WhatsApp:**

1. **Sync Contacts:**
   - Нажать "Синхронизировать контакты"
   - Проверить что контакты появились в `/api/contacts`

2. **Sync Chat History:**
   - Выбрать чат из списка
   - Нажать "Скачать историю"
   - Проверить сообщения в `/api/messages`

3. **Send Message:**
   - Отправить тестовое сообщение
   - Проверить доставку в WhatsApp

4. **Receive Message:**
   - Отправить сообщение из WhatsApp на подключенный номер
   - Проверить webhook получил событие
   - Проверить сообщение появилось в БД

---

## Critical Files to Modify/Create

### Backend Files (7 new, 4 modified)

**New:**
1. `backend/app/models/evolution.py` - Evolution instance model
2. `backend/app/services/evolution.py` - Evolution API service layer (~400-500 строк)
3. `backend/app/api/evolution.py` - Evolution API routes
4. `alembic/versions/<timestamp>_add_evolution_api_support.py` - DB migration

**Modified:**
5. `backend/app/core/config.py` - Add Evolution settings
6. `backend/app/models/whatsapp.py` - Add Evolution fields
7. `backend/app/models/__init__.py` - Import EvolutionInstance
8. `backend/app/api/routes.py` - Add Evolution webhook
9. `backend/app/main.py` - Register Evolution router
10. `backend/.env.example` - Add Evolution variables

### Frontend Files (2 new, 1 modified)

**New:**
11. `frontend/src/app/whatsapp/page.tsx` - WhatsApp connection page
12. `frontend/src/app/whatsapp/sync/page.tsx` - Chat sync page

**Modified:**
13. `frontend/src/lib/api.ts` - Add Evolution API client, fix hardcoded URL

### Infrastructure Files (2 new, 1 modified)

**New:**
14. `.github/workflows/deploy.yml` - GitHub Actions CI/CD
15. `.env` - Production environment (на VM, не в Git)

**Modified:**
16. `deploy/gcp-setup.sh` - Update PROJECT_ID, INSTANCE_NAME

---

## Deployment Checklist

**Обозначения:** 👤 User tasks | 🤖 Claude tasks

### Pre-Deployment

- [ ] 👤 GCP Project создан
- [ ] 👤 Billing account настроен (для free tier тоже нужен)
- [ ] 👤 gcloud CLI установлен и настроен (`gcloud init`)
- [ ] 👤 GitHub repository создан (если еще нет)
- [ ] 👤 SSH ключи для GitHub Actions сгенерированы

### Infrastructure Setup

- [ ] 👤 GCP VM создан (e2-micro, us-west1-b) - через deploy/gcp-setup.sh
- [ ] 👤 Firewall rules настроены (HTTP, HTTPS) - автоматически через скрипт
- [ ] 👤 External IP получен
- [ ] 👤 Domain указывает на IP (если используется domain)
- [ ] 👤 SSH доступ к VM работает
- [ ] 👤 Docker + Docker Compose установлены - через deploy/server-setup.sh
- [ ] 👤 2GB swap создан - автоматически через server-setup.sh
- [ ] 👤 Git установлен - автоматически через server-setup.sh

### Application Setup

- [ ] 👤 Repository склонирован на VM
- [ ] 👤 `.env` файл создан с production значениями
- [ ] 👤 SECRET_KEY и EVOLUTION_API_KEY сгенерированы (openssl rand -hex 32)
- [ ] 👤 SSL сертификаты получены (Let's Encrypt certbot)
- [ ] 👤 docker-compose.prod.yml запущен
- [ ] 👤 Все контейнеры running (5 контейнеров) - проверить через docker ps

### Database

- [ ] 👤 PostgreSQL контейнер running
- [ ] 🤖👤 Database migrations выполнены - Claude создает, User запускает на prod
- [ ] 👤 Таблицы созданы - проверить через psql
- [ ] 👤 Test user создан и может login

### GitHub Actions

- [ ] 🤖 .github/workflows/deploy.yml создан - Claude
- [ ] 👤 GitHub Secrets настроены (GCP_VM_IP, GCP_VM_USER, GCP_SSH_KEY)
- [ ] 👤 SSH key добавлен в VM ~/.ssh/authorized_keys
- [ ] 👤 Test push в main branch запускает deployment
- [ ] 👤 Workflow успешно выполняется - проверить в GitHub Actions tab

### Testing

- [ ] 👤 Frontend доступен (https://domain или http://ip)
- [ ] 👤 Backend API работает (/api/health, /api/docs)
- [ ] 👤 User registration работает
- [ ] 👤 User login работает
- [ ] 👤 Evolution instance creation работает
- [ ] 👤 QR код отображается
- [ ] 👤 WhatsApp подключение работает (сканирование QR своим телефоном)
- [ ] 👤 Contact sync работает
- [ ] 👤 Message history sync работает
- [ ] 👤 Send message работает
- [ ] 👤 Webhook получает incoming messages

### Monitoring

- [ ] 👤 Docker logs доступны (`docker-compose logs`)
- [ ] 👤 Nginx access/error logs работают
- [ ] 👤 Database queries работают
- [ ] 👤 Disk space проверен (`df -h`)
- [ ] 👤 Memory usage проверен (`free -h`)
- [ ] 👤 Swap usage проверен (`swapon --show`)

---

## Success Criteria

План считается успешно выполненным когда:

1. ✅ **Evolution API интегрирован**
   - Backend код взаимодействует с Evolution API
   - QR код подключение работает
   - История чатов скачивается

2. ✅ **GCP Deployment работает**
   - VM e2-micro running
   - Все 5 Docker контейнеров running
   - HTTPS доступен (если настроен SSL)

3. ✅ **CI/CD автоматизирован**
   - Push в main автоматически деплоит
   - Zero-downtime updates

4. ✅ **Приложение функционирует**
   - User registration/login
   - WhatsApp подключение
   - Contact sync
   - Message sync
   - Send/receive messages

5. ✅ **Performance приемлемый**
   - Frontend loads < 3s
   - API response < 500ms
   - No memory issues на e2-micro

---

## Estimated Costs

| Компонент | Стоимость |
|-----------|-----------|
| GCP e2-micro VM | $0/месяц (free tier) |
| 30GB pd-standard disk | $0/месяц (free tier включает 30GB) |
| Outbound traffic | $0 для первых 1GB, потом $0.12/GB |
| **Total** | **~$0-5/месяц** |

Free tier limits:
- 1 e2-micro instance в us-west1, us-central1, или us-east1
- 30 GB-months standard persistent disk
- 1 GB network egress per month

Для MVP это полностью бесплатно если traffic < 1GB/месяц.

---

## Potential Issues & Mitigations

### Issue 1: QR Code Expires
**Проблема:** QR код Evolution API истекает через 40-60 секунд

**Решение:**
- Auto-refresh QR каждые 30 секунд во frontend
- Показывать countdown timer
- Webhook обновляет QR в БД при событии `qrcode.updated`

### Issue 2: Memory Issues on e2-micro
**Проблема:** 1GB RAM может быть недостаточно для 5 контейнеров

**Решение:**
- 2GB swap файл уже настроен в server-setup.sh
- Memory limits в docker-compose.prod.yml оптимизированы
- Monitoring swap usage: `swapon --show`
- При необходимости: upgrade до e2-small ($15/месяц)

### Issue 3: Evolution Instance Disconnects
**Проблема:** WhatsApp может отключиться при долгом неиспользовании

**Решение:**
- Webhook слушает `connection.update` событие
- Обновляет `status` в `evolution_instances` таблице
- Frontend показывает уведомление пользователю
- Пользователь может пересканировать QR код

### Issue 4: Duplicate Messages
**Проблема:** Сообщения могут дублироваться между Evolution и Cloud API

**Решение:**
- Используем `evolution_key_id` для дедупликации
- При sync проверяем существование message перед insert
- `sync_message_to_db()` метод в evolution.py handle этого

### Issue 5: Database Growth
**Проблема:** История чатов может быстро заполнить disk

**Решение:**
- Limit sync history до последних **30 сообщений** per chat
- Pagination при sync больших чатов
- Archive старых messages (>**2 years**) в отдельную таблицу или удалять
- Monitor disk usage: `df -h`

---

## Post-Deployment Maintenance

### Regular Tasks

**Weekly:**
- Проверить disk space (`df -h`)
- Проверить docker logs на errors
- Backup PostgreSQL database:
  ```bash
  docker exec wa_postgres pg_dump -U wa_user wa_database > backup_$(date +%Y%m%d).sql
  ```

**Monthly:**
- Обновить SSL сертификаты (Let's Encrypt auto-renew)
- Проверить security updates: `sudo apt update && sudo apt upgrade -y`
- Очистить старые Docker images: `docker system prune -a`

**As Needed:**
- Monitor memory usage
- Rotate logs если накапливаются
- Archive old messages если БД растет

### Troubleshooting Commands

```bash
# Check all containers
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f evolution

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend

# Check database
docker exec -it wa_postgres psql -U wa_user -d wa_database

# Check resources
df -h           # Disk
free -h         # Memory
swapon --show   # Swap
```

---

## Next Steps After MVP

Когда приложение стабильно и набирает пользователей:

1. **Migrate to Cloud SQL** (~$10/месяц)
   - Managed PostgreSQL
   - Automatic backups
   - High availability

2. **Add Cloud Run** (~$20/месяц)
   - Auto-scaling
   - Zero maintenance
   - Pay per use

3. **Setup Monitoring** (бесплатно)
   - Cloud Monitoring
   - Cloud Logging
   - Alerts

4. **Add Secret Manager** ($0.06 per secret/месяц)
   - Secure credentials
   - Rotation support

5. **CDN для Static Assets**
   - Cloud Storage + Cloud CDN
   - Faster loading globally
