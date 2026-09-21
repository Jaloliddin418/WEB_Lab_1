# Структура проекта

## Дерево файлов

```
timemanager/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   └── models.py
│   ├── schemas/
│   │   └── schemas.py
│   ├── services/
│   │   ├── auth.py
│   │   └── dependencies.py
│   └── routers/
│       ├── auth.py
│       ├── tasks.py
│       ├── categories.py
│       ├── tags.py
│       ├── time_entries.py
│       ├── schedules.py
│       └── analytics.py
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_initial.py
├── alembic.ini
├── requirements.txt
└── .env
```

## Слои приложения

Код разделён на слои, у каждого одна зона ответственности.

| Слой | Папка / файл | Ответственность |
|------|--------------|-----------------|
| Настройки | `config.py` | Чтение параметров из `.env`: адрес БД, секретный ключ, время жизни токена |
| Подключение к БД | `database.py` | Движок SQLAlchemy, фабрика сессий, базовый класс моделей, `get_db()` |
| Модели | `models/` | Описание таблиц базы данных |
| Схемы | `schemas/` | Контракт API: что принимаем и что отдаём, валидация |
| Сервисы | `services/` | Хеширование, JWT, получение текущего пользователя |
| Роутеры | `routers/` | HTTP-эндпоинты, разбиты по предметным областям |
| Точка входа | `main.py` | Сборка приложения и подключение роутеров |
| Миграции | `alembic/` | История изменений схемы БД |

## Как файлы связаны между собой

```mermaid
flowchart TD
    ENV[.env] --> CONFIG[config.py]
    CONFIG --> DB[database.py]
    CONFIG --> AUTH_S[services/auth.py]
    DB --> MODELS[models/models.py]
    MODELS --> SCHEMAS[schemas/schemas.py]
    MODELS --> AUTH_S
    AUTH_S --> DEPS[services/dependencies.py]
    DB --> DEPS
    MODELS --> ROUTERS[routers/*.py]
    SCHEMAS --> ROUTERS
    DEPS --> ROUTERS
    DB --> ROUTERS
    ROUTERS --> MAIN[main.py]
    MODELS --> ALEMBIC[alembic/env.py]
    CONFIG --> ALEMBIC
```

## Что происходит при запуске

При выполнении `uvicorn app.main:app` Python раскручивает цепочку импортов, и модули выполняются снизу вверх:

1. `config.py` - создаётся объект `settings`, значения подставляются из `.env`
2. `database.py` - создаётся `engine` и фабрика сессий `SessionLocal`
3. `models/models.py` - все таблицы регистрируются в `Base.metadata`
4. `schemas/schemas.py` - Pydantic компилирует схемы валидации
5. `services/` - инициализируются bcrypt-контекст и схема OAuth2
6. `routers/` - каждый файл создаёт `APIRouter` и регистрирует эндпоинты
7. `main.py` - создаётся `app`, к нему подключаются все роутеры
8. Uvicorn запускает сервер на порту 8000

!!! warning "Таблицы при запуске не создаются"
    Приложение только подключается к базе. Структура таблиц создаётся отдельно - командой `alembic upgrade head`.

## Путь одного запроса

```mermaid
sequenceDiagram
    participant C as Клиент
    participant F as FastAPI
    participant D as Зависимости
    participant P as Pydantic
    participant R as Роутер
    participant DB as PostgreSQL

    C->>F: POST /tasks/ + Bearer токен
    F->>D: get_db()
    D-->>F: сессия
    F->>D: get_current_user()
    D->>DB: поиск пользователя из токена
    DB-->>D: User
    F->>P: валидация тела по TaskCreate
    P-->>F: data
    F->>R: create_task(data, db, user)
    R->>DB: INSERT INTO tasks
    DB-->>R: id, created_at
    R-->>F: объект Task
    F->>P: фильтрация по TaskOut
    F-->>C: 201 Created + JSON
```

## Настройки через .env

```
DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5432/time_manager_db
SECRET_KEY=supersecretkey1234567890abcdef
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

В `config.py` заданы значения по умолчанию, а `.env` их перекрывает. Файл `.env` не попадает в git - пароли и секретный ключ остаются только на локальной машине.
