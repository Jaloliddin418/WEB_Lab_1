# ORM-модели

Модели описаны в `app/models/models.py` с использованием синтаксиса SQLAlchemy 2.0.

## Подключение к базе

```python title="app/database.py"
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- `engine` - подключение к PostgreSQL, создаётся один раз
- `SessionLocal` - фабрика сессий, на каждый запрос создаётся новая
- `Base` - все модели наследуются от него, по этому признаку SQLAlchemy находит таблицы
- `get_db()` - генератор: отдаёт сессию эндпоинту и гарантированно закрывает её в `finally`, даже при ошибке

## Синтаксис описания колонок

```python
id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
```

- `Mapped[int]` - тип в Python, используется редактором и анализаторами
- `mapped_column(...)` - описание колонки в БД: тип и ограничения

| Параметр | Значение |
|----------|----------|
| `primary_key=True` | Первичный ключ |
| `index=True` | Индекс для быстрого поиска |
| `unique=True` | Значение уникально в таблице |
| `nullable=False` | Поле обязательно |
| `default=...` | Значение по умолчанию |
| `onupdate=...` | Значение, подставляемое при каждом обновлении строки |
| `ForeignKey("table.col")` | Внешний ключ |

## Колонка и relationship

```python title="Task"
owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
owner: Mapped["User"] = relationship("User", back_populates="tasks")
```

```python title="User"
tasks: Mapped[list["Task"]] = relationship("Task", back_populates="owner")
```

- `owner_id` - **реальная колонка** в таблице `tasks`
- `owner` и `tasks` - **не колонки**, а связи на уровне Python. SQLAlchemy по ним сам подгружает связанные объекты
- `back_populates` связывает обе стороны: `user.tasks` возвращает список задач, `task.owner` - владельца

## Модель Task

```python title="app/models/models.py"
class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.medium)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.pending)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    schedule_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("daily_schedules.id"), nullable=True)

    owner: Mapped["User"] = relationship("User", back_populates="tasks")
    category: Mapped["Category | None"] = relationship("Category", back_populates="tasks")
    schedule: Mapped["DailySchedule | None"] = relationship("DailySchedule", back_populates="tasks")
    time_entries: Mapped[list["TimeEntry"]] = relationship("TimeEntry", back_populates="task")
    task_tags: Mapped[list["TaskTag"]] = relationship("TaskTag", back_populates="task")
```

Центральная модель проекта. Имеет три внешних ключа и пять связей:

| Связь | Возвращает | Сторона |
|-------|------------|---------|
| `owner` | один `User` | many |
| `category` | одна `Category` или `None` | many |
| `schedule` | одно `DailySchedule` или `None` | many |
| `time_entries` | список `TimeEntry` | one |
| `task_tags` | список `TaskTag` | one |

## Ассоциативная сущность TaskTag

```python title="app/models/models.py"
class TaskTag(Base):
    __tablename__ = "task_tags"

    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    task: Mapped["Task"] = relationship("Task", back_populates="task_tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="task_tags")
```

- `primary_key=True` у двух полей - составной первичный ключ
- `added_at` - поле, характеризующее связь
- Связь many-to-many оформлена как отдельная модель, а не как `secondary`-таблица, именно потому что у связи есть собственные данные

## Модель TimeEntry

```python title="app/models/models.py"
class TimeEntry(Base):
    __tablename__ = "time_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)
    note: Mapped[str | None] = mapped_column(String(256), nullable=True)

    task: Mapped["Task"] = relationship("Task", back_populates="time_entries")
```

Каждая сессия работы над задачей - отдельная запись. Если `ended_at` пустой, работа ещё идёт и длительность не считается.
