"""
Shared utilities and configuration for API Gateway
"""
import os
import logging
from typing import Dict, Any
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GatewayConfig:
    """Configuration management for API Gateway"""
    
    def __init__(self):
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        self.cors_credentials = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.gateway_port = int(os.getenv("GATEWAY_PORT", "8080"))
        self.gateway_host = os.getenv("GATEWAY_HOST", "0.0.0.0")
        
        # Rate limiting configuration
        self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        
        # Security configuration
        self.security_headers_enabled = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
        self.api_key_header = os.getenv("API_KEY_HEADER", "X-API-Key")

class HealthResponse(BaseModel):
    """Response model for health checks"""
    status: str
    services: Dict[str, Dict[str, str]]
    version: str = "1.0.0"
    timestamp: str

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    message: str
    status_code: int
    timestamp: str

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    data: Any = None
    error: str = None
    message: str = None

def get_gateway_config() -> GatewayConfig:
    """Get gateway configuration instance"""
    return GatewayConfig()

def setup_cors_middleware(app, config: GatewayConfig):
    """Setup CORS middleware with configuration"""
    from fastapi.middleware.cors import CORSMiddleware
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=config.cors_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )

def setup_security_headers_middleware(app, config: GatewayConfig):
    """Setup security headers middleware"""
    if not config.security_headers_enabled:
        return
    
    from fastapi import Request, Response
    
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

def create_error_response(error: str, message: str, status_code: int) -> ErrorResponse:
    """Create standardized error response"""
    from datetime import datetime
    return ErrorResponse(
        error=error,
        message=message,
        status_code=status_code,
        timestamp=datetime.utcnow().isoformat()
    )

def create_api_response(success: bool = True, data: Any = None, error: str = None, message: str = None) -> APIResponse:
    """Create standardized API response"""
    return APIResponse(
        success=success,
        data=data,
        error=error,
        message=message
    )