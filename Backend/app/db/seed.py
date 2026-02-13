from sqlalchemy.orm import Session

from app.models.role import Role

DEFAULT_ROLES = ("user", "admin")


def seed_default_roles(db: Session) -> None:
    existing = db.query(Role).filter(Role.name.in_(DEFAULT_ROLES)).all()
    existing_names = {role.name for role in existing}

    to_create = [Role(name=name) for name in DEFAULT_ROLES if name not in existing_names]
    if to_create:
        db.add_all(to_create)
        db.commit()
