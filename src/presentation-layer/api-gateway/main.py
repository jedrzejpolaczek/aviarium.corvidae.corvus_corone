from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import logging
import httpx
import os

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
    "orchestrator": "http://experiment-orchestrator:8000",
    "tracking": "http://experiment-tracking:8002",
    "registry": "http://algorithm-registry:8004",
    "analysis": "http://metrics-analysis:8005",
    "benchmarks": "http://benchmark-definition:8003",
    "reports": "http://report-generator:8007",
    "publications": "http://publication-service:8006"
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

# Experiment routes (temporarily without auth for testing)
@app.api_route("/api/experiments", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_experiments_base(request: Request):
    """Proxy experiment-related requests (base path)"""
    # Route to orchestrator for creation/management, tracking for queries and deletion
    if request.method in ["POST", "PUT"]:
        service = "orchestrator"
        target_path = "/api/experiments"
    else:
        service = "tracking"
        target_path = "/api/tracking/experiments"
    
    return await service_router.proxy_request(service, target_path, request)

@app.api_route("/api/experiments/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_experiments(path: str, request: Request):
    """Proxy experiment-related requests"""
    # Route to orchestrator for creation/management, tracking for queries and deletion
    if request.method in ["POST", "PUT"]:
        service = "orchestrator"
        target_path = f"/api/experiments/{path}"
    else:
        service = "tracking"
        target_path = f"/api/tracking/experiments/{path}"
    
    return await service_router.proxy_request(service, target_path, request)

# Tracking routes
@app.api_route("/api/tracking/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_tracking(path: str, request: Request, user=Depends(auth_component.verify_token)):
    """Proxy tracking requests"""
    return await service_router.proxy_request("tracking", f"/api/tracking/{path}", request)

# Algorithm registry routes (temporarily without auth for testing)
@app.api_route("/api/algorithms", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_algorithms_base(request: Request):
    """Proxy algorithm registry requests (base path)"""
    return await service_router.proxy_request("algorithms", "/api/algorithms", request)

@app.api_route("/api/algorithms/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_algorithms(path: str, request: Request):
    """Proxy algorithm registry requests"""
    return await service_router.proxy_request("algorithms", f"/api/algorithms/{path}", request)

# Metrics and analysis routes
@app.api_route("/api/metrics/{path:path}", methods=["GET", "POST"])
async def proxy_metrics(path: str, request: Request, user=Depends(auth_component.verify_token)):
    """Proxy metrics analysis requests"""
    return await service_router.proxy_request("analysis", f"/api/metrics/{path}", request)

# Benchmark routes (temporarily without auth for testing)
@app.api_route("/api/benchmarks", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_benchmarks_base(request: Request):
    """Proxy benchmark requests (base path)"""
    return await service_router.proxy_request("benchmarks", "/api/benchmarks", request)

@app.api_route("/api/benchmarks/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_benchmarks(path: str, request: Request):
    """Proxy benchmark requests"""
    return await service_router.proxy_request("benchmarks", f"/api/benchmarks/{path}", request)

# Publication routes
@app.api_route("/api/publications/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_publications(path: str, request: Request, user=Depends(auth_component.verify_token)):
    """Proxy publication requests"""
    return await service_router.proxy_request("publications", f"/api/publications/{path}", request)

# Experiment control endpoints - Route to orchestrator service
@app.post("/api/experiments/{experiment_id}/start")
async def start_experiment(experiment_id: str, request: Request):
    """Start an experiment"""
    return await service_router.proxy_request("orchestrator", f"/api/experiments/{experiment_id}/start", request)

@app.post("/api/experiments/{experiment_id}/pause")
async def pause_experiment(experiment_id: str, request: Request):
    """Pause an experiment"""
    return await service_router.proxy_request("orchestrator", f"/api/experiments/{experiment_id}/pause", request)

@app.post("/api/experiments/{experiment_id}/cancel")
async def cancel_experiment(experiment_id: str, request: Request):
    """Cancel an experiment"""
    return await service_router.proxy_request("orchestrator", f"/api/experiments/{experiment_id}/cancel", request)

@app.get("/api/experiments/{experiment_id}/runs")
async def get_experiment_runs(experiment_id: str, request: Request):
    """Get runs for an experiment"""
    return await service_router.proxy_request("tracking", f"/api/experiments/{experiment_id}/runs", request)

@app.get("/api/experiments/{experiment_id}/metrics")
async def get_experiment_metrics(experiment_id: str, request: Request):
    """Get metrics for an experiment"""
    return await service_router.proxy_request("tracking", f"/api/experiments/{experiment_id}/metrics", request)

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

# Static file serving for web UI
@app.get("/")
async def serve_index():
    """Serve the main web UI"""
    web_ui_path = "/app/web-ui"
    index_path = os.path.join(web_ui_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        # Fallback to a simple response if file doesn't exist
        return {"message": "Web UI not found", "status": "error"}

# Mount static files
web_ui_path = "/app/web-ui"
if os.path.exists(web_ui_path):
    app.mount("/static", StaticFiles(directory=web_ui_path), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)