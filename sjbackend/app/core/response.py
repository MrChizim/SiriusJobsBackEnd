# app/core/response.py
from typing import Generic, TypeVar, Optional, Any
from fastapi.responses import JSONResponse
from fastapi import status
from pydantic import BaseModel

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    """Standard API response format for v2"""
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
    errors: Optional[list] = None
    meta: Optional[dict] = None

def success_response(
    data: Any = None,
    message: str = None,
    meta: dict = None,
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    Generate a standardized success response.
    
    Example:
    {
        "success": true,
        "message": "Operation successful",
        "data": { ... },
        "meta": { "page": 1, "total": 100 }
    }
    """
    content = {
        "success": True,
        "data": data
    }
    
    if message:
        content["message"] = message
    
    if meta:
        content["meta"] = meta
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )

def error_response(
    error: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    errors: list = None
) -> JSONResponse:
    """
    Generate a standardized error response.
    
    Example:
    {
        "success": false,
        "error": "Validation failed",
        "errors": [
            { "field": "email", "message": "Invalid email" }
        ]
    }
    """
    content = {
        "success": False,
        "error": error
    }
    
    if errors:
        content["errors"] = errors
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )

def paginated_response(
    items: list,
    total: int,
    page: int,
    limit: int,
    message: str = None
) -> JSONResponse:
    """
    Generate a paginated response with metadata.
    """
    pages = (total + limit - 1) // limit
    
    return success_response(
        data=items,
        message=message,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1
        }
    )