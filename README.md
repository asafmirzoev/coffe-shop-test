# coffe-shop-test

## Описание

Это backend-сервис, реализованный на FastAPI. Основные возможности:
- Регистрация и аутентификация пользователей (JWT)
- Управление пользователями (админ/обычный пользователь)
- Кеширование данных в Redis
- Хранение данных в PostgreSQL
- Асинхронная работа с базой данных через SQLAlchemy

## Структура проекта

```
app/
  api/         # REST API роутеры (auth, users)
  cache/       # Работа с кешем Redis (модели, репозитории)
  core/        # Базовые настройки, контейнер зависимостей, обработка ошибок
  db/          # Модели и репозитории для работы с PostgreSQL
  schemas/     # Pydantic-схемы для валидации запросов/ответов
  services/    # Бизнес-логика (auth, users)
  unions/      # Слой объединения кеша и базы данных
```

## Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/asafmirzoev/coffe-shop-test.git
cd coffe-shop-test
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе `.env.template` и заполните необходимые значения (Postgres, Redis, JWT и др).

### 3. Запуск через Docker Compose

```bash
docker-compose up --build
```

- Приложение будет доступно на http://localhost:8000
- Документация Swagger: http://localhost:8000/docs (если включён debug)
   ```

## Переменные окружения

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` — настройки PostgreSQL
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_USERNAME`, `REDIS_PASSWORD`, `REDIS_DB_PASSWORD` — настройки Redis
- `JWT_SECRETKEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_LIFETIME`, `REFRESH_TOKEN_LIFETIME` — параметры JWT
- `ADMIN_EMAIL` — email администратора

Все переменные перечислены в `.env.template`.

---

**Автор:** Asaf Mirzoev