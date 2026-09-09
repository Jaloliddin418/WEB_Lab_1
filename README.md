# Time Manager API

FastAPI приложение для управления задачами и временем.

## Стек

- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0** - ORM
- **Alembic** - миграции
- **PostgreSQL** - база данных
- **JWT (python-jose)** - аутентификация
- **passlib[bcrypt]** - хеширование паролей

---

## Модель данных

### Таблицы

| Таблица | Описание |
|---------|----------|
| `users` | Пользователи системы |
| `categories` | Категории задач (one-to-many с tasks) |
| `tags` | Теги (many-to-many с tasks) |
| `tasks` | Задачи с приоритетом, дедлайном и статусом |
| `task_tags` | Ассоциативная сущность Task-Tag (поле `added_at`) |
| `time_entries` | Записи о затраченном времени (one-to-many с tasks) |
| `daily_schedules` | Ежедневные расписания (one-to-many с tasks) |

### Связи

- **one-to-many**: User -> Tasks, User -> Categories, User -> DailySchedules
- **one-to-many**: Category -> Tasks, DailySchedule -> Tasks
- **one-to-many**: Task -> TimeEntries
- **many-to-many**: Task <-> Tag через `task_tags`
- **Ассоциативная сущность** `task_tags` содержит поле `added_at` - момент добавления тега к задаче

---

## Запуск через Docker

```bash
cp .env .env
docker-compose up --build
```

## Запуск локально

```bash
# Создать БД PostgreSQL
createdb timemanager

cp .env .env
pip install -r requirements.txt

alembic upgrade head
uvicorn app.main:app --reload
```

Документация: http://localhost:8000/docs

---

## API Endpoints

### Auth
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register` | Регистрация |
| POST | `/auth/login` | Получение JWT токена |
| GET | `/auth/me` | Информация о текущем пользователе |
| GET | `/auth/users` | Список всех пользователей |
| PATCH | `/auth/me/password` | Смена пароля |

### Tasks
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/tasks/` | Создать задачу |
| GET | `/tasks/` | Список задач (фильтры: status, priority, category_id, overdue_only) |
| GET | `/tasks/upcoming-deadlines` | Задачи с дедлайном в ближайшие N часов |
| GET | `/tasks/{id}` | Получить задачу с вложенными объектами |
| PUT | `/tasks/{id}` | Обновить задачу |
| DELETE | `/tasks/{id}` | Удалить задачу |
| POST | `/tasks/{id}/tags/{tag_id}` | Добавить тег к задаче |
| DELETE | `/tasks/{id}/tags/{tag_id}` | Убрать тег с задачи |

### Time Entries
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/tasks/{id}/time-entries/` | Записать время |
| GET | `/tasks/{id}/time-entries/` | Список записей времени |
| DELETE | `/tasks/{id}/time-entries/{entry_id}` | Удалить запись |

### Categories / Tags / Schedules
Полный CRUD на `/categories/`, `/tags/`, `/schedules/`

### Analytics
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/analytics/` | Общая статистика: кол-во задач, просроченных, суммарное время по задачам |

---

## Структура проекта

```
timemanager/
├── app/
│   ├── main.py              # Точка входа FastAPI
│   ├── config.py            # Настройки (pydantic-settings)
│   ├── database.py          # SQLAlchemy engine + get_db
│   ├── models/
│   │   └── models.py        # Все ORM-модели
│   ├── schemas/
│   │   └── schemas.py       # Pydantic схемы (in/out)
│   ├── routers/
│   │   ├── auth.py          # Регистрация, логин, смена пароля
│   │   ├── tasks.py         # CRUD задач + теги + дедлайн-уведомления
│   │   ├── categories.py    # CRUD категорий
│   │   ├── tags.py          # CRUD тегов
│   │   ├── time_entries.py  # Учёт времени
│   │   ├── schedules.py     # Ежедневные расписания
│   │   └── analytics.py     # Аналитика времени
│   └── services/
│       ├── auth.py          # JWT + bcrypt
│       └── dependencies.py  # get_current_user
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_initial.py   # Миграция создания всех таблиц
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```
