# Запуск и демонстрация

## Требования

- Python 3.11 или 3.12
- PostgreSQL

!!! warning "Версия Python"
    На Python 3.14 пакеты `psycopg2-binary` и `pydantic-core` могут не устанавливаться - для них ещё нет готовых сборок.

## Установка

**1. Создать виртуальное окружение и установить зависимости**

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**2. Создать базу данных**

В pgAdmin: **Databases → Create → Database**, имя `time_manager_db`.

**3. Создать файл `.env`** в корне проекта

```
DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5432/time_manager_db
SECRET_KEY=supersecretkey1234567890abcdef
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Файл нужно сохранить в кодировке UTF-8.

**4. Применить миграции**

```bash
python -m alembic upgrade head
```

**5. Запустить сервер**

```bash
python -m uvicorn app.main:app --reload
```

Документация: `http://localhost:8000/docs`

## Сценарий демонстрации

### 1. Регистрация

`POST /auth/register`

```json
{"username": "andrew", "email": "andrew@example.com", "password": "secret123"}
```

В ответе нет пароля - схема `UserOut` его не содержит.

### 2. Вход и авторизация

1. Нажать **Authorize** вверху страницы Swagger
2. Ввести `username` и `password`, остальные поля оставить пустыми
3. Swagger сам вызовет `POST /auth/login` и будет подставлять токен во все запросы

### 3. Справочники

`POST /categories/`

```json
{"name": "Учёба", "color": "#22c55e"}
```

`POST /tags/`

```json
{"name": "срочно"}
```

### 4. Задача

`POST /tasks/`

```json
{
  "title": "Сдать лабораторную",
  "description": "FastAPI + PostgreSQL",
  "priority": "high",
  "deadline": "2026-09-25T18:00:00",
  "category_id": 1
}
```

### 5. Many-to-many

`POST /tasks/1/tags/1` - прикрепить тег к задаче.

В ответе в `task_tags` появится объект с вложенным тегом и полем `added_at`.

### 6. Учёт времени

`POST /tasks/1/time-entries/`

```json
{
  "started_at": "2026-09-21T10:00:00",
  "ended_at": "2026-09-21T11:30:00",
  "note": "Модели и миграции"
}
```

`duration_minutes` будет равен `90.0` - вычислено на сервере.

### 7. Вложенные объекты

`GET /tasks/1` - задача целиком: категория, теги и записи времени.

### 8. Дедлайны и аналитика

- `GET /tasks/upcoming-deadlines?hours=168` - задачи с дедлайном на неделю вперёд
- `GET /analytics/` - статистика по задачам и времени

### 9. Методы пользователя

- `GET /auth/me` - текущий пользователь
- `GET /auth/users` - список пользователей
- `PATCH /auth/me/password` - смена пароля

### 10. Проверка защиты

Нажать **Authorize → Logout** и повторить любой запрос к `/tasks/` - ответ `401 Unauthorized`.

## Типичные проблемы

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `alembic` / `uvicorn` не распознано | Скрипты не в PATH | Запускать через `python -m` |
| `No module named ...` | Зависимость не установилась | `pip install -r requirements.txt` |
| `UnicodeDecodeError` при подключении | Кодировка `.env` или кириллица в пароле | Пересохранить `.env` в UTF-8, пароль латиницей |
| `password cannot be longer than 72 bytes` | Несовместимость passlib и новой bcrypt | `pip install bcrypt==4.0.1` |
| `email-validator is not installed` | Нужен для `EmailStr` | `pip install email-validator` |
