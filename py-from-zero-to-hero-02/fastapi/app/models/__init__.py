# Centralized model imports for SQLAlchemy mapper registration.
# Importing this package ensures both classes are loaded before
# relationship resolution (e.g., "Sku" <-> "UnitOfMeasurement").
from app.models.sku import Sku
from app.models.uom import UnitOfMeasurement

# Re-export model classes used by the application bootstrap.
__all__ = ["Sku", "UnitOfMeasurement"]
