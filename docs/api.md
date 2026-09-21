# API-эндпоинты

Интерактивная документация доступна после запуска по адресу `http://localhost:8000/docs`.

Все эндпоинты, кроме `/auth/register` и `/auth/login`, требуют заголовок `Authorization: Bearer <token>`.

## Сводная таблица

=== "Задачи"

    | Метод | Путь | Описание |
    |-------|------|----------|
    | POST | `/tasks/` | Создать задачу |
    | GET | `/tasks/` | Список задач с фильтрами |
    | GET | `/tasks/upcoming-deadlines` | Задачи с дедлайном в ближайшие N часов |
    | GET | `/tasks/{task_id}` | Задача с вложенными объектами |
    | PUT | `/tasks/{task_id}` | Частичное обновление |
    | DELETE | `/tasks/{task_id}` | Удалить задачу |
    | POST | `/tasks/{task_id}/tags/{tag_id}` | Прикрепить тег |
    | DELETE | `/tasks/{task_id}/tags/{tag_id}` | Открепить тег |

=== "Учёт времени"

    | Метод | Путь | Описание |
    |-------|------|----------|
    | POST | `/tasks/{task_id}/time-entries/` | Добавить запись времени |
    | GET | `/tasks/{task_id}/time-entries/` | Записи времени задачи |
    | DELETE | `/tasks/{task_id}/time-entries/{entry_id}` | Удалить запись |

=== "Справочники"

    | Метод | Путь | Описание |
    |-------|------|----------|
    | POST / GET | `/categories/` | Создать / список категорий |
    | GET / PUT / DELETE | `/categories/{id}` | Операции с категорией |
    | POST / GET | `/tags/` | Создать / список тегов |
    | GET / DELETE | `/tags/{id}` | Операции с тегом |
    | POST / GET | `/schedules/` | Создать / список расписаний |
    | GET / DELETE | `/schedules/{id}` | Расписание с задачами дня |

=== "Аналитика"

    | Метод | Путь | Описание |
    |-------|------|----------|
    | GET | `/analytics/` | Статистика по задачам и затраченному времени |

## Создание задачи

```python title="app/routers/tasks.py"
@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskOut:
    task = Task(**data.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

- `owner_id` берётся из токена, а не из тела запроса - нельзя создать задачу от чужого имени
- `db.refresh()` подтягивает значения, сгенерированные базой: `id` и `created_at`

## Фильтрация списка

```python title="app/routers/tasks.py"
@router.get("/", response_model=list[TaskOut])
def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    overdue_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskOut]:
    q = db.query(Task).filter(Task.owner_id == current_user.id)
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == priority)
    if category_id:
        q = q.filter(Task.category_id == category_id)
    if overdue_only:
        q = q.filter(Task.deadline < datetime.utcnow(), Task.status != "done")
    return q.all()
```

Запрос собирается по частям: каждый `filter()` добавляет условие `AND`. SQL выполняется один раз - при вызове `.all()`.

Пример: `GET /tasks/?status=pending&priority=high`

## Уведомления о дедлайнах

```python title="app/routers/tasks.py"
@router.get("/upcoming-deadlines", response_model=list[TaskOut])
def upcoming_deadlines(
    hours: int = Query(24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskOut]:
    now = datetime.utcnow()
    threshold = now + timedelta(hours=hours)
    return (
        db.query(Task)
        .filter(
            Task.owner_id == current_user.id,
            Task.deadline >= now,
            Task.deadline <= threshold,
            Task.status != "done",
        )
        .order_by(Task.deadline)
        .all()
    )
```

Возвращает невыполненные задачи, дедлайн которых попадает в окно `[сейчас; сейчас + N часов]`, самые срочные первыми.

!!! warning "Порядок объявления маршрутов"
    `/upcoming-deadlines` объявлен выше `/{task_id}`. FastAPI проверяет маршруты сверху вниз, и `{task_id}` перехватил бы строку `upcoming-deadlines`, после чего запрос упал бы на преобразовании в `int`.

## Частичное обновление

```python title="app/routers/tasks.py"
for field, value in data.model_dump(exclude_none=True).items():
    setattr(task, field, value)
```

`exclude_none=True` оставляет только переданные поля, `setattr` устанавливает их по имени. Клиент может прислать только `{"status": "done"}`.

## Работа с ассоциативной сущностью

```python title="app/routers/tasks.py"
already = db.query(TaskTag).filter(TaskTag.task_id == task_id, TaskTag.tag_id == tag_id).first()
if not already:
    task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
    db.add(task_tag)
    db.commit()
```

Прикрепление тега создаёт строку в `task_tags`, поле `added_at` заполняется автоматически. Перед созданием проверяется, что такой связи ещё нет. При откреплении удаляется только строка связи - задача и тег остаются.

## Учёт времени

```python title="app/routers/time_entries.py"
duration = None
if data.ended_at:
    delta = data.ended_at - data.started_at
    duration = delta.total_seconds() / 60
```

Длительность вычисляется на сервере из разности `datetime`. Если `ended_at` не передан, длительность остаётся пустой.

## Аналитика

```python title="app/routers/analytics.py"
total_tasks = len(tasks)
done_tasks = sum(1 for t in tasks if t.status == TaskStatus.done)
overdue_tasks = sum(
    1 for t in tasks
    if t.deadline and t.deadline < now and t.status != TaskStatus.done
)
```

Ответ содержит общее число задач, выполненные, просроченные, суммарное время и разбивку по задачам, отсортированную по убыванию затраченного времени.

```json
{
  "total_tasks": 5,
  "done_tasks": 2,
  "overdue_tasks": 1,
  "total_tracked_minutes": 185.5,
  "per_task": [
    {"task_id": 1, "title": "Написать отчёт", "total_minutes": 120.0, "entry_count": 3},
    {"task_id": 4, "title": "Подготовить слайды", "total_minutes": 65.5, "entry_count": 2}
  ]
}
```

## Изоляция данных пользователей

Во всех запросах к задачам присутствует фильтр `Task.owner_id == current_user.id`. Обращение к чужой задаче возвращает 404 - пользователь не может ни прочитать, ни изменить чужие данные и даже не узнаёт об их существовании.
