from typing import Dict, Any, Generic, TypeVar
import logging
from backend.core.exceptions import BaseAppException, handle_exception

logger = logging.getLogger(__name__)

# Type variable for generic service
T = TypeVar('T')

class BaseService(Generic[T]):
    """Base service class with common operations and error handling"""
    
    def __init__(self, repository=None):
        self.repository = repository
    
    def handle_errors(self, operation_name: str):
        """Decorator for handling errors in service methods"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except BaseAppException as e:
                    logger.error(f"{operation_name} failed: {str(e)}")
                    raise
                except Exception as e:
                    logger.exception(f"Unexpected error in {operation_name}: {str(e)}")
                    raise handle_exception(e)
            return wrapper
        return decorator
    
    def log_operation(self, operation_name: str, **params):
        """Log an operation with its parameters"""
        param_str = ", ".join(f"{k}={v}" for k, v in params.items())
        logger.info(f"Executing {operation_name}: {param_str}")