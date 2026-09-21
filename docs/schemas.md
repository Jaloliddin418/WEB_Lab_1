# Pydantic-схемы

Схемы описаны в `app/schemas/schemas.py`. Модели описывают, что лежит в базе, а схемы - что приходит от клиента и что уходит клиенту.

## Зачем отдельный слой схем

| Задача | Пример |
|--------|--------|
| Валидация входа | `title` должен быть строкой, `priority` - одним из допустимых значений. Иначе ответ 422 |
| Защита выхода | `UserOut` не содержит `hashed_password`, поэтому хеш не попадёт в ответ |
| Контроль возможностей клиента | В `TaskCreate` нет `status` - нельзя создать задачу сразу выполненной |
| Документация | Swagger UI строится автоматически по схемам |

## Три схемы на одну сущность

```python title="app/schemas/schemas.py"
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.medium
    deadline: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    category_id: Optional[int] = None
    schedule_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[TaskStatus] = None
    deadline: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    category_id: Optional[int] = None
    schedule_id: Optional[int] = None
```

| Схема | Назначение | Особенность |
|-------|------------|-------------|
| `TaskCreate` | Создание | Обязателен только `title`, поля `status` нет |
| `TaskUpdate` | Изменение | Все поля необязательны - частичное обновление |
| `TaskOut` | Ответ | Содержит вложенные объекты |

## Вложенные объекты

```python title="app/schemas/schemas.py"
class TaskTagOut(BaseModel):
    tag_id: int
    tag: TagOut
    added_at: datetime

    model_config = {"from_attributes": True}


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: Priority
    status: TaskStatus
    deadline: Optional[datetime]
    estimated_minutes: Optional[int]
    created_at: datetime
    updated_at: datetime
    owner_id: int
    category_id: Optional[int]
    schedule_id: Optional[int]
    category: Optional[CategoryOut]
    task_tags: list[TaskTagOut]
    time_entries: list[TimeEntryOut]

    model_config = {"from_attributes": True}
```

Последние три поля `TaskOut` реализуют требование о GET-запросах с вложенными объектами:

- `category` - связь one-to-many, отдаётся весь объект категории, а не только `category_id`
- `task_tags` - связь many-to-many, каждый элемент содержит объект тега и поле `added_at`
- `time_entries` - связь one-to-many, все записи времени задачи

Вложенность работает за счёт связки двух механизмов: `relationship()` в модели подгружает связанные объекты, а вложенная схема описывает, как их сериализовать.

`model_config = {"from_attributes": True}` разрешает Pydantic читать данные из атрибутов объекта SQLAlchemy (`task.title`), а не только из словаря.

## Пример ответа

```json
{
  "id": 1,
  "title": "Написать отчёт",
  "description": null,
  "priority": "high",
  "status": "in_progress",
  "deadline": "2024-06-01T18:00:00",
  "estimated_minutes": 120,
  "created_at": "2024-05-20T14:23:11",
  "updated_at": "2024-05-21T09:10:00",
  "owner_id": 1,
  "category_id": 2,
  "schedule_id": null,
  "category": {"id": 2, "name": "Работа", "color": "#ff0000", "user_id": 1},
  "task_tags": [
    {"tag_id": 5, "tag": {"id": 5, "name": "срочно"}, "added_at": "2024-05-20T14:25:00"}
  ],
  "time_entries": [
    {
      "id": 3,
      "task_id": 1,
      "started_at": "2024-05-21T08:40:00",
      "ended_at": "2024-05-21T09:10:00",
      "duration_minutes": 30.0,
      "note": "Черновик"
    }
  ]
}
```

## Схемы пользователя

```python title="app/schemas/schemas.py"
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str
```

`EmailStr` автоматически проверяет формат email. В `UserOut` пароля нет ни в каком виде.
