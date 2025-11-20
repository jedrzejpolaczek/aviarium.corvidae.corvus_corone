"""
Authentication and authorization components for API Gateway
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

class AuthenticationComponent:
    """Handles authentication and authorization for API Gateway"""
    
    def __init__(self):
        self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[Dict[str, Any]]:
        """Verify JWT token with auth service"""
        if not credentials:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.auth_service_url}/verify",
                    headers={"Authorization": f"Bearer {credentials.credentials}"},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Token verification failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Auth service communication error: {e}")
            return None
    
    async def require_auth(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Require valid authentication, raise 401 if not authenticated"""
        user = await self.verify_token(credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def require_role(self, required_role: str, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Require specific role, raise 403 if insufficient permissions"""
        user = await self.require_auth(credentials)
        user_roles = user.get("roles", [])
        
        if required_role not in user_roles and "admin" not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role '{required_role}' not found"
            )
        return user

# Global instance
auth_component = AuthenticationComponent()