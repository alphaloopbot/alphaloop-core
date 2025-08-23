"""Base model for AlphaLoop Storage."""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class BaseModel(Base):
    """Base model with common fields and methods."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseModel":
        """Create model instance from dictionary."""
        # Filter out None values and convert datetime strings
        filtered_data = {}
        for key, value in data.items():
            if value is not None:
                if key in ["created_at", "updated_at"] and isinstance(value, str):
                    try:
                        filtered_data[key] = datetime.fromisoformat(
                            value.replace("Z", "+00:00")
                        )
                    except ValueError:
                        # Skip invalid datetime strings
                        continue
                else:
                    filtered_data[key] = value

        return cls(**filtered_data)

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
