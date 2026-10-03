"""Rotas de CRUD de tarefas, isoladas por usuário autenticado."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from taskflow.api.deps import CurrentUser, DbSession
from taskflow.models import Task
from taskflow.schemas import TaskCreate, TaskList, TaskPublic, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_owned_task(task_id: int, user_id: int, db: DbSession) -> Task:
    """Busca uma tarefa garantindo que ela pertence ao usuário logado."""
    task = db.scalar(select(Task).where(Task.id == task_id, Task.owner_id == user_id))
    if task is None:
        # 404 em vez de 403 para não revelar que a tarefa existe mas é de outro usuário.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada",
        )
    return task


@router.post("", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: DbSession, user: CurrentUser) -> Task:
    """Cria uma nova tarefa para o usuário autenticado."""
    task = Task(**payload.model_dump(), owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=TaskList)
def list_tasks(
    db: DbSession,
    user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Quantidade de registros a pular"),
    limit: int = Query(default=50, ge=1, le=200, description="Máximo de registros por página"),
    completed: bool | None = Query(default=None, description="Filtra por status"),
) -> TaskList:
    """Lista as tarefas do usuário com paginação e filtro opcional."""
    filters = [Task.owner_id == user.id]
    if completed is not None:
        filters.append(Task.completed.is_(completed))

    total = db.scalar(select(func.count()).select_from(Task).where(*filters)) or 0
    rows = db.scalars(
        select(Task).where(*filters).order_by(Task.created_at.desc()).offset(skip).limit(limit)
    ).all()

    items = [TaskPublic.model_validate(row) for row in rows]
    return TaskList(total=total, skip=skip, limit=limit, items=items)


@router.get("/{task_id}", response_model=TaskPublic)
def get_task(task_id: int, db: DbSession, user: CurrentUser) -> Task:
    """Retorna uma tarefa específica do usuário."""
    return _get_owned_task(task_id, user.id, db)


@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(task_id: int, payload: TaskUpdate, db: DbSession, user: CurrentUser) -> Task:
    """Atualiza parcialmente uma tarefa."""
    task = _get_owned_task(task_id, user.id, db)
    changes = payload.model_dump(exclude_unset=True)

    if changes.get("completed") is True and not task.completed:
        task.completed_at = datetime.now(UTC)
    elif changes.get("completed") is False:
        task.completed_at = None

    for field, value in changes.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: DbSession, user: CurrentUser) -> None:
    """Remove uma tarefa pertencente ao usuário."""
    task = _get_owned_task(task_id, user.id, db)
    db.delete(task)
    db.commit()
