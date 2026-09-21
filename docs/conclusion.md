# Вывод

В ходе работы разработано серверное приложение тайм-менеджера на FastAPI с хранением данных в PostgreSQL. Модель данных из 7 таблиц описана средствами ORM SQLAlchemy, схема базы разворачивается миграциями Alembic. Реализованы CRUD-операции, GET-запросы с вложенными объектами, учёт времени, уведомления о дедлайнах, ежедневные расписания и аналитика. Доступ к данным защищён JWT-аутентификацией, пароли хранятся в виде bcrypt-хешей.

## Соответствие критериям модели данных

| Требование | Реализация |
|------------|------------|
| 5 или больше таблиц | 7 таблиц: `users`, `categories`, `tags`, `tasks`, `task_tags`, `time_entries`, `daily_schedules` |
| Связи one-to-many | 6 связей, например `User → Tasks` через `tasks.owner_id` |
| Связь many-to-many | `Task ↔ Tag` через `task_tags` |
| Поле, характеризующее связь | `task_tags.added_at` |

## Соответствие заданию на 9 баллов

| Требование | Где реализовано |
|------------|-----------------|
| Таблицы через SQLAlchemy + PostgreSQL | `app/models/models.py`, `app/database.py` |
| CRUD | `app/routers/` - задачи, категории, теги, расписания, записи времени |
| GET с вложенными объектами | `TaskOut` в `app/schemas/schemas.py`: `category`, `task_tags`, `time_entries` |
| Миграции Alembic | `alembic/versions/001_initial.py` |
| Аннотация типов | Pydantic-схемы и type hints во всех эндпоинтах |
| Файловая структура | Слои `models`, `schemas`, `services`, `routers` |

## Соответствие заданию на 15 баллов

| Требование | Где реализовано |
|------------|-----------------|
| Регистрация и авторизация | `POST /auth/register`, `POST /auth/login` |
| Генерация JWT | `create_access_token()` в `app/services/auth.py` |
| Аутентификация по JWT | `get_current_user()` в `app/services/dependencies.py` |
| Хеширование паролей | `hash_password()`, `verify_password()` на bcrypt |
| Дополнительные методы | `GET /auth/me`, `GET /auth/users`, `PATCH /auth/me/password` |

## Соответствие предметной области

| Функция | Реализация |
|---------|------------|
| Задачи с описанием | `title`, `description` в `tasks` |
| Сроки выполнения | `deadline` |
| Приоритеты | `priority` - enum из 4 значений |
| Учёт затраченного времени | `time_entries`, автоматический расчёт `duration_minutes` |
| Уведомления о дедлайнах | `GET /tasks/upcoming-deadlines` |
| Ежедневное расписание | `daily_schedules`, эндпоинты `/schedules/` |
| Анализ затраченного времени | `GET /analytics/` |
