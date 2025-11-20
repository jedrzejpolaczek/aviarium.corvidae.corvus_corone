from fastapi import FastAPI, Request, Depends, HTTPException
from datetime import datetime
import logging
import httpx

# Import components and shared utilities
from components import auth_component, service_router
from shared import (
    get_gateway_config,
    setup_cors_middleware,
    setup_security_headers_middleware,
    HealthResponse,
    create_api_response
)

# Configure logging
config = get_gateway_config()
logging.basicConfig(level=getattr(logging, config.log_level))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Corvus Corone - API Gateway",
    description="Central API Gateway for HPO Benchmarking Platform",
    version="1.0.0"
)

# Setup middleware
setup_cors_middleware(app, config)
setup_security_headers_middleware(app, config)

# Service URLs
SERVICE_URLS = {
    "auth": "http://auth-service:8001",
    "orchestrator": "http://experiment-orchestrator:8002",
    "tracking": "http://experiment-tracking:8003",
    "registry": "http://algorithm-registry:8004",
    "analysis": "http://metrics-analysis:8005",
    "benchmarks": "http://benchmark-definition:8006",
    "reports": "http://report-generator:8007",
    "publications": "http://publication-service:8008"
}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = await service_router.health_check_all()
    
    return HealthResponse(
        status="ok",
        services=services,
        timestamp=datetime.utcnow().isoformat()
    )

# Experiment routes
@app.api_route("/api/experiments/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_experiments(path: str, request: Request, user=Depends(auth_component.verify_token)):
    """Proxy experiment-related requests"""
    # Route to orchestrator for creation/management, tracking for queries
    if request.method in ["POST", "PUT", "DELETE"]:
        service = "orchestrator"
    else:
        service = "tracking"
    
    return await service_router.proxy_request(service, f"/api/experiments/{path}", request)

# Tracking routes
@app.api_route("/api/tracking/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_tracking(path: str, request: Request, user=Depends(auth_component.verify_token)):
    """Proxy tracking requests"""
    return await service_router.proxy_request("tracking", f"/api/tracking/{path}", request)

# Algorithm registry routes
@app.api_route("/api/algorithms/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_algorithms(path: str, request: Request, user=Depends(auth_component.verify_token)):
    """Proxy algorithm registry requests"""
    return await service_router.proxy_request("registry", f"/api/algorithms/{path}", request)

# Metrics and analysis routes
@app.api_route("/api/metrics/{path:path}", methods=["GET", "POST"])
async def proxy_metrics(path: str, request: Request, user=Depends(auth_component.verify_token)):
    """Proxy metrics analysis requests"""
    return await service_router.proxy_request("analysis", f"/api/metrics/{path}", request)

# Benchmark routes
@app.api_route("/api/benchmarks/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_benchmarks(path: str, request: Request, user=Depends(auth_component.verify_token)):
    """Proxy benchmark requests"""
    return await service_router.proxy_request("benchmarks", f"/api/benchmarks/{path}", request)

# Publication routes
@app.api_route("/api/publications/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_publications(path: str, request: Request, user=Depends(auth_component.verify_token)):
    """Proxy publication requests"""
    return await service_router.proxy_request("publications", f"/api/publications/{path}", request)

# Report generation routes
@app.api_route("/api/reports/{path:path}", methods=["GET", "POST"])
async def proxy_reports(path: str, request: Request, user=Depends(auth_component.verify_token)):
    """Proxy report generation requests"""
    return await service_router.proxy_request("reports", f"/api/reports/{path}", request)

# Authentication routes (no auth required for auth itself)
@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_auth(path: str, request: Request):
    """Proxy authentication requests"""
    return await service_router.proxy_request("auth", f"/api/auth/{path}", request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)