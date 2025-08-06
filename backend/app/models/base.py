"""
Base database model configuration
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String, func
import uuid

Base = declarative_base()


class BaseModel:
    """Base model with common fields"""
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    created_at = Column(
        DateTime,
        default=func.datetime('now'),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=func.datetime('now'),
        onupdate=func.datetime('now'),
        nullable=False
    )