#!/bin/bash

# Corvus Corone Development Setup Script
# This script sets up the development environment

set -e

echo "🐦 Setting up Corvus Corone development environment..."

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/minio
mkdir -p data/grafana
mkdir -p src/support-layer/infrastructure/monitoring/dashboards

# Set permissions
chmod 755 logs
chmod 755 data

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Corvus Corone Environment Configuration

# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/corvus_corone

# Message Broker
RABBITMQ_URL=amqp://admin:admin@rabbitmq:5672

# Object Storage
OBJECT_STORAGE_URL=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Authentication
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# Development Settings
DEBUG=true
LOG_LEVEL=INFO

# Service URLs (internal)
API_GATEWAY_URL=http://api-gateway:8080
TRACKING_SERVICE_URL=http://experiment-tracking:8002
BENCHMARK_SERVICE_URL=http://benchmark-definition:8003
ALGORITHM_REGISTRY_URL=http://algorithm-registry:8004
METRICS_SERVICE_URL=http://metrics-analysis:8005
PUBLICATION_SERVICE_URL=http://publication-service:8006
REPORT_SERVICE_URL=http://report-generator:8007
AUTH_SERVICE_URL=http://auth-service:8001
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Build images
echo "🔨 Building Docker images..."
docker-compose build --parallel

echo "✅ Development environment setup complete!"
echo ""
echo "🚀 To start the system:"
echo "   npm run start"
echo ""
echo "🌐 Once running, access:"
echo "   • Web UI: http://localhost:3000"
echo "   • API Gateway: http://localhost:8080"
echo "   • RabbitMQ Management: http://localhost:15672 (admin/admin)"
echo "   • MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo "   • Grafana: http://localhost:3001 (admin/admin)"
echo "   • Prometheus: http://localhost:9090"
echo ""
echo "📖 Documentation: docs/README.docs.md"
echo "🐛 Logs: npm run logs"
echo "🛑 Stop: npm run stop"