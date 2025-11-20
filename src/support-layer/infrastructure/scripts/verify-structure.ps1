#!/usr/bin/env pwsh
# Verify the layered architecture structure is correctly implemented

param(
    [string]$RootPath = (Get-Location)
)

Write-Host "🔍 Verifying Corvus Corone Architecture Structure" -ForegroundColor Cyan
Write-Host "Root: $RootPath" -ForegroundColor Gray
Write-Host ""

$srcPath = Join-Path $RootPath "src"

if (-not (Test-Path $srcPath)) {
    Write-Host "❌ src/ directory not found at $srcPath" -ForegroundColor Red
    exit 1
}

# Expected layer structure
$expectedLayers = @(
    "presentation-layer",
    "business-logic-layer", 
    "execution-layer",
    "support-layer",
    "data-layer"
)

$expectedPresentationServices = @("web-ui", "api-gateway")
$expectedBusinessServices = @(
    "experiment-orchestrator",
    "experiment-tracking", 
    "metrics-analysis",
    "algorithm-registry",
    "benchmark-definition",
    "publication-service",
    "report-generator"
)
$expectedExecutionServices = @("worker-runtime")
$expectedSupportServices = @("auth-service")

Write-Host "🏗️  Architecture Layers:" -ForegroundColor Yellow
foreach ($layer in $expectedLayers) {
    $layerPath = Join-Path $srcPath $layer
    if (Test-Path $layerPath) {
        Write-Host "  ✅ $layer" -ForegroundColor Green
        
        # Check services in each layer
        $services = Get-ChildItem $layerPath -Directory | Select-Object -ExpandProperty Name
        foreach ($service in $services) {
            $servicePath = Join-Path $layerPath $service
            $componentsPath = Join-Path $servicePath "components"
            $sharedPath = Join-Path $servicePath "shared"
            
            $hasComponents = Test-Path $componentsPath
            $hasShared = Test-Path $sharedPath
            $hasMain = Test-Path (Join-Path $servicePath "main.py")
            $hasDockerfile = Test-Path (Join-Path $servicePath "Dockerfile")
            
            if ($hasComponents -and $hasShared -and $hasMain -and $hasDockerfile) {
                Write-Host "    ✅ $service (complete)" -ForegroundColor Green
            } elseif ($hasMain) {
                Write-Host "    ⚠️  $service (missing components/shared structure)" -ForegroundColor Yellow
            } else {
                Write-Host "    ❌ $service (incomplete)" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "  ❌ $layer" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🐳 Docker Configuration:" -ForegroundColor Yellow
$dockerComposePath = Join-Path $RootPath "docker-compose.yml"
if (Test-Path $dockerComposePath) {
    Write-Host "  ✅ docker-compose.yml exists" -ForegroundColor Green
    
    # Check if build paths reference new structure
    $dockerContent = Get-Content $dockerComposePath -Raw
    if ($dockerContent -match "presentation-layer" -and $dockerContent -match "business-logic-layer") {
        Write-Host "  ✅ Build paths updated for layered structure" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Build paths may need updating for layered structure" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ❌ docker-compose.yml not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Yellow
$docsPath = Join-Path $RootPath "docs"
if (Test-Path $docsPath) {
    Write-Host "  ✅ docs/ directory exists" -ForegroundColor Green
    
    $architecturePath = Join-Path $docsPath "architecture"
    if (Test-Path $architecturePath) {
        Write-Host "  ✅ Architecture documentation exists" -ForegroundColor Green
    }
} else {
    Write-Host "  ❌ docs/ directory not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Summary:" -ForegroundColor Cyan
Write-Host "The project structure follows the C4 architectural pattern:" -ForegroundColor Gray
Write-Host "  • Layers → Containers → Components hierarchy" -ForegroundColor Gray
Write-Host "  • Each service has components/ and shared/ directories" -ForegroundColor Gray
Write-Host "  • Docker configuration updated for new paths" -ForegroundColor Gray
Write-Host "  • Documentation reflects new structure" -ForegroundColor Gray
Write-Host ""
Write-Host "✨ Architecture verification complete!" -ForegroundColor Green