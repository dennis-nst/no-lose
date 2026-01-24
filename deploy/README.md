# Deploy to Google Cloud e2-micro (Free Tier)

## Prerequisites

1. Google Cloud аккаунт с активированным биллингом
2. Установленный [gcloud CLI](https://cloud.google.com/sdk/docs/install)
3. Git репозиторий с вашим проектом

## Шаг 1: Настройка gcloud

```bash
# Авторизация
gcloud auth login

# Создание проекта (или используйте существующий)
gcloud projects create your-project-id --name="WA App"

# Установка проекта по умолчанию
gcloud config set project your-project-id

# Включение Compute Engine API
gcloud services enable compute.googleapis.com
```

## Шаг 2: Создание VM

Отредактируйте `gcp-setup.sh`:
- Замените `PROJECT_ID` на ваш ID проекта

```bash
chmod +x gcp-setup.sh
./gcp-setup.sh
```

## Шаг 3: Настройка сервера

```bash
# SSH на сервер
gcloud compute ssh wa-app --zone=us-west1-b

# Скачать и запустить скрипт настройки
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/server-setup.sh | bash

# Выйти и зайти снова для применения прав Docker
exit
gcloud compute ssh wa-app --zone=us-west1-b
```

## Шаг 4: Деплой приложения

```bash
# Клонировать репозиторий
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git app
cd app

# Создать .env файл
cp .env.example .env
nano .env
```

Заполните `.env`:
```env
DOMAIN=YOUR_EXTERNAL_IP.nip.io
EVOLUTION_API_KEY=generate-random-string-here
```

> Tip: Используйте `openssl rand -hex 32` для генерации API ключа

```bash
# Запуск
docker-compose -f docker-compose.prod.yml up -d --build

# Проверка логов
docker-compose -f docker-compose.prod.yml logs -f
```

## Шаг 5: Настройка домена (опционально)

1. Получите внешний IP:
```bash
gcloud compute instances describe wa-app --zone=us-west1-b --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

2. Настройте DNS A-запись вашего домена на этот IP

3. Добавьте SSL с Let's Encrypt (см. раздел ниже)

## Добавление SSL (Let's Encrypt)

```bash
# На сервере
sudo apt install certbot

# Остановить nginx
docker-compose -f docker-compose.prod.yml stop nginx

# Получить сертификат
sudo certbot certonly --standalone -d your-domain.com

# Скопировать сертификаты
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/

# Обновить nginx.conf для HTTPS и запустить
docker-compose -f docker-compose.prod.yml up -d nginx
```

## Полезные команды

```bash
# Статус контейнеров
docker-compose -f docker-compose.prod.yml ps

# Логи конкретного сервиса
docker-compose -f docker-compose.prod.yml logs -f evolution

# Перезапуск
docker-compose -f docker-compose.prod.yml restart

# Остановка
docker-compose -f docker-compose.prod.yml down

# Обновление (после git pull)
docker-compose -f docker-compose.prod.yml up -d --build
```

## Использование памяти (e2-micro: 1GB RAM)

| Сервис | Лимит |
|--------|-------|
| PostgreSQL | 200 MB |
| Evolution API | 350 MB |
| Backend | 150 MB |
| Frontend | 200 MB |
| Nginx | 64 MB |
| **Swap** | 2 GB |

> Swap критически важен для e2-micro!

## Troubleshooting

**Out of memory:**
```bash
# Проверить swap
free -h

# Если swap не активен
sudo swapon /swapfile
```

**Контейнер перезапускается:**
```bash
docker logs wa_evolution --tail 100
```

**Не работает webhook:**
- Проверьте что домен доступен извне
- Проверьте логи nginx: `docker logs wa_nginx`
