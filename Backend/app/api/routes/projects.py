from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


def _get_project_or_404(db: Session, project_id: int) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.is_active.is_(True))
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


def _ensure_owner_or_admin(project: Project, current_user: User) -> None:
    if current_user.role.name != "admin" and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a project owned by the current user."""
    project = Project(
        name=payload.name,
        description=payload.description,
        owner_id=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse], status_code=status.HTTP_200_OK)
def list_projects(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List active projects visible to the current user."""
    query = db.query(Project).filter(Project.is_active.is_(True))
    if current_user.role.name != "admin":
        query = query.filter(Project.owner_id == current_user.id)
    return query.offset(offset).limit(limit).all()


@router.get("/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single project (owner or admin)."""
    project = _get_project_or_404(db, project_id)
    _ensure_owner_or_admin(project, current_user)
    return project


@router.put("/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a project (owner or admin)."""
    project = _get_project_or_404(db, project_id)
    _ensure_owner_or_admin(project, current_user)

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a project (owner or admin)."""
    project = _get_project_or_404(db, project_id)
    _ensure_owner_or_admin(project, current_user)

    project.is_active = False
    db.commit()
    db.refresh(project)
    return project
