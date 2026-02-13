from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models to ensure they are registered with SQLAlchemy metadata.
from app.models.user import User  # noqa: F401
from app.models.role import Role  # noqa: F401
