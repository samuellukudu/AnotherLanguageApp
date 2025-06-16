from typing import Dict, Any, Optional
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class BaseAppException(Exception):
    """Base exception class for application-specific exceptions"""
    def __init__(self, 
                 message: str, 
                 status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
        
    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException"""
        return HTTPException(
            status_code=self.status_code,
            detail={
                "message": self.message,
                "details": self.details
            }
        )

class DatabaseException(BaseAppException):
    """Exception for database-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )
        logger.error(f"Database error: {message}")

class ResourceNotFoundException(BaseAppException):
    """Exception for when a requested resource is not found"""
    def __init__(self, resource_type: str, resource_id: Any, details: Optional[Dict[str, Any]] = None):
        message = f"{resource_type} with id {resource_id} not found"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )
        logger.warning(f"Resource not found: {message}")

class ValidationException(BaseAppException):
    """Exception for validation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )
        logger.warning(f"Validation error: {message}")

class AuthenticationException(BaseAppException):
    """Exception for authentication errors"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )
        logger.warning(f"Authentication error: {message}")

class AuthorizationException(BaseAppException):
    """Exception for authorization errors"""
    def __init__(self, message: str = "Not authorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )
        logger.warning(f"Authorization error: {message}")

class AIServiceException(BaseAppException):
    """Exception for AI service errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )
        logger.error(f"AI Service error: {message}")

class ConfigurationException(BaseAppException):
    """Exception for configuration errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )
        logger.error(f"Configuration error: {message}")

def handle_exception(exc: Exception) -> HTTPException:
    """Convert any exception to an appropriate HTTPException"""
    if isinstance(exc, BaseAppException):
        return exc.to_http_exception()
    
    # Log unexpected exceptions
    logger.exception("Unhandled exception occurred")
    
    # Return a generic error for unexpected exceptions
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "message": "An unexpected error occurred",
            "details": {"error_type": type(exc).__name__}
        }
    )