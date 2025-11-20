"""
__init__.py for API Gateway components
"""
from .auth import auth_component, AuthenticationComponent
from .routing import service_router, ServiceRouter

__all__ = [
    "auth_component",
    "AuthenticationComponent", 
    "service_router",
    "ServiceRouter"
]