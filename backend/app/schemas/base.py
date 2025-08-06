"""
Base Pydantic schemas and common models
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Optional, List
from datetime import datetime
from uuid import UUID


class BaseResponse(BaseModel):
    """Base response model with common metadata"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseResponse):
    """Success response with data payload"""
    data: Optional[Dict[str, Any]] = None


class Position3D(BaseModel):
    """3D position coordinates"""
    x: float = Field(..., description="X coordinate in 3D space")
    y: float = Field(..., description="Y coordinate in 3D space") 
    z: float = Field(..., description="Z coordinate in 3D space")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "x": 10.5,
                "y": 5.2,
                "z": -3.7
            }
        }
    )


class TimestampMixin(BaseModel):
    """Mixin for models with timestamps"""
    created_at: datetime
    updated_at: datetime


class UUIDMixin(BaseModel):
    """Mixin for models with UUID primary key"""
    id: UUID


class PaginationParams(BaseModel):
    """Common pagination parameters"""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")
    
    @property
    def offset(self) -> int:
        """Calculate database offset from page parameters"""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseResponse):
    """Paginated response wrapper"""
    items: List[Any] = []
    total_count: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    
    @classmethod
    def create(cls, items: List[Any], total_count: int, pagination: PaginationParams):
        """Create paginated response from items and pagination params"""
        total_pages = (total_count + pagination.page_size - 1) // pagination.page_size
        
        return cls(
            items=items,
            total_count=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages
        )


class SortParams(BaseModel):
    """Common sorting parameters"""
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")


class DateRangeFilter(BaseModel):
    """Date range filtering"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None