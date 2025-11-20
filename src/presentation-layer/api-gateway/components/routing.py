"""
Service routing and proxy components for API Gateway
"""
import httpx
import os
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from fastapi.responses import Response

logger = logging.getLogger(__name__)

class ServiceRouter:
    """Handles routing and proxying requests to backend services"""
    
    def __init__(self):
        self.service_urls = {
            "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
            "orchestrator": os.getenv("ORCHESTRATOR_SERVICE_URL", "http://experiment-orchestrator:8000"),
            "tracking": os.getenv("TRACKING_SERVICE_URL", "http://experiment-tracking:8002"),
            "metrics": os.getenv("METRICS_SERVICE_URL", "http://metrics-analysis:8005"),
            "benchmarks": os.getenv("BENCHMARK_SERVICE_URL", "http://benchmark-definition:8003"),
            "algorithms": os.getenv("ALGORITHM_REGISTRY_URL", "http://algorithm-registry:8004"),
            "publications": os.getenv("PUBLICATION_SERVICE_URL", "http://publication-service:8006"),
            "reports": os.getenv("REPORT_SERVICE_URL", "http://report-generator:8007")
        }
    
    async def proxy_request(self, service_name: str, path: str, request: Request, **kwargs) -> Response:
        """Proxy request to backend service"""
        if service_name not in self.service_urls:
            raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
        
        service_url = self.service_urls[service_name]
        target_url = f"{service_url}{path}"
        
        try:
            # Forward request headers (excluding host)
            headers = dict(request.headers)
            headers.pop("host", None)
            
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    params=request.query_params,
                    headers=headers,
                    content=await request.body(),
                    timeout=30.0,
                    **kwargs
                )
                
                # Forward response headers (excluding server-specific ones)
                response_headers = dict(response.headers)
                for header in ["server", "date", "content-encoding", "transfer-encoding", "connection"]:
                    response_headers.pop(header, None)
                
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=response_headers,
                    media_type=response.headers.get("content-type")
                )
                
        except httpx.TimeoutException:
            logger.error(f"Timeout when connecting to {service_name} service")
            raise HTTPException(status_code=504, detail=f"{service_name} service timeout")
        except httpx.ConnectError:
            logger.error(f"Failed to connect to {service_name} service")
            raise HTTPException(status_code=503, detail=f"{service_name} service unavailable")
        except Exception as e:
            logger.error(f"Error proxying request to {service_name}: {e}")
            raise HTTPException(status_code=502, detail=f"Error communicating with {service_name} service")
    
    async def health_check_service(self, service_name: str) -> Dict[str, str]:
        """Check health of a specific service"""
        if service_name not in self.service_urls:
            return {"status": "unknown", "message": "Service not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.service_urls[service_name]}/health",
                    timeout=5.0
                )
                if response.status_code == 200:
                    return {"status": "healthy", "message": "Service is responding"}
                else:
                    return {"status": "unhealthy", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def health_check_all(self) -> Dict[str, Dict[str, str]]:
        """Check health of all configured services"""
        results = {}
        for service_name in self.service_urls.keys():
            results[service_name] = await self.health_check_service(service_name)
        return results

# Global instance
service_router = ServiceRouter()