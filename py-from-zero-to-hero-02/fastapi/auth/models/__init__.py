# Centralized model imports for SQLAlchemy mapper registration.
# Importing this package ensures both classes are loaded before
# any relationship resolution
from auth.models.user import User

# Re-export model classes used by the application bootstrap.
__all__ = ["User"]
