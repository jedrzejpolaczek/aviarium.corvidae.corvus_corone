# Corvus Corone - HPO Benchmarking Platform

> **A comprehensive platform for benchmarking Hyperparameter Optimization (HPO) algorithms**

[![Architecture Status](https://img.shields.io/badge/Architecture-Layered%20%2B%20Validated-green)](./IMPLEMENTATION_SUMMARY.md)
[![Documentation](https://img.shields.io/badge/Documentation-Complete-blue)](./docs/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](./docker-compose.yml)
[![Tests](https://img.shields.io/badge/Tests-Integration%20%2B%20Performance-green)](./tests/)

**Production-ready platform** for benchmarking hyperparameter optimization (HPO) algorithms with emphasis on reproducibility, statistical rigor, and scalable architecture. Implements a **layered microservices architecture** following the C4 model with comprehensive validation and testing.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- 8GB+ RAM recommended

### Local Development Setup

```bash
# Clone repository (already done if you're reading this)
cd aviarium.corvidae.corvus_corone

# Start all services
docker-compose up -d

# Wait for services to be ready (takes 2-3 minutes)
# Check status
docker-compose ps

# Validate architecture implementation
python src/support-layer/infrastructure/scripts/validate-architecture.py

# Access the application
# Web UI: http://localhost:8080 (unified access via API Gateway)
# API Endpoints: http://localhost:8080/api/
# API Documentation: http://localhost:8080/docs
# RabbitMQ Management: http://localhost:15672 (admin/admin)
# MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
# Grafana: http://localhost:3001 (admin/admin)
```

> **Architecture Note**: The Web UI is served directly by the API Gateway at port 8080, providing a unified access point that simplifies deployment and reduces port conflicts.

### Your First Experiment

1. **Open Web UI**: Navigate to http://localhost:8080
2. **Create Experiment**: Click "New Experiment"
3. **Select Benchmark**: Choose from UCI datasets or synthetic problems
4. **Choose Algorithms**: Select algorithms to compare (e.g., Random Search vs Bayesian Optimization)
5. **Configure**: Set budget limits and seeds
6. **Run**: Start the experiment and monitor progress
7. **Analyze**: View results, comparisons, and statistical tests

## Documentation

**Production-ready documentation** of the system has been organized into an easy-to-navigate structure:

**[Start here - Documentation Guide](docs/README.docs.md)**

**Complete documentation includes:**
- **Requirements**: Use cases, functional and non-functional requirements + Requirements Traceability Matrix
- **Architecture**: Full C4 model (Context, Containers, Components, Code) 
- **Design Decisions**: **12 complete ADRs** covering all key architectural decisions
- **Operations**: Deployment examples, monitoring, **performance benchmarks & SLA definitions**
- **Methodology**: Benchmarking practices, research methodologies
- **User Guides**: Workflows, usage instructions

### Quick links:
- [Use Cases](docs/requirements/use-cases.md) - Requirements and scenarios
- [System Architecture](docs/architecture/c1-context.md) - Technical overview (C4 Model)
- [Layer Documentation](docs/architecture/layers/) - Detailed layer specifications
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Architecture implementation details
- [Deployment Guide](docs/operations/deployment-guide.md) - Setup and deployment instructions
- [Architecture Validation](src/support-layer/infrastructure/scripts/validate-architecture.py) - Automated architecture testing

---

*Detailed navigation and description of all documents: [docs/README.docs.md](docs/README.docs.md)*

## Project Data

**Project name:** Corvus Corone  
**Application name:** HPO Benchmarking Platform  
**Architecture:** Layered Microservices (C4 Model)  
**Software version:** 1.0.0  
**Implementation Status:** Complete with Validation  
**Repository Purpose:** Production-ready HPO algorithms benchmarking platform with layered architecture

## Table of Contents

1. [Documentation](#-documentation)
2. [Project Data](#project-data)
3. [System Architecture](#-system-architecture)
4. [Technologies](#-technologies)
5. [Project Structure](#-project-structure)
6. [Installation and Setup](#-installation-and-setup)
7. [Contributing](#-contributing)
8. [License](#-license)

## System Architecture

Corvus Corone implements a **layered microservices architecture** following the C4 model:

### **Layered Architecture** (Layers → Containers → Components)
- **Presentation Layer**: Web UI + API Gateway for external interfaces
- **Business Logic Layer**: Core domain services (Experiment Orchestrator, Tracking, Analysis, etc.)
- **Execution Layer**: HPO algorithm runtime and worker management
- **Support Layer**: Cross-cutting services (Authentication, Monitoring)
- **Data Layer**: Persistent storage and data management

### **Technology Stack**
- **Container orchestration**: Docker Compose (dev) + Kubernetes (prod)
- **Message broker**: RabbitMQ for asynchronous communication
- **Storage**: PostgreSQL (primary), Object Storage (artifacts), Redis (cache)
- **Monitoring**: Prometheus + Grafana with distributed tracing

**Complete details**: [Architecture Documentation](docs/architecture/c1-context.md) | [Layer Guide](docs/architecture/layers/)

## Technologies

### Backend
- **Python 3.9+** - Core application language
- **FastAPI** - API framework
- **SQLAlchemy** - ORM
- **Celery** - Task queue
- **Docker** - Containerization

### Databases
- **PostgreSQL** - Primary transactional data
- **ClickHouse** - Analytics and time-series data
- **Redis** - Caching and real-time data
- **InfluxDB** - Monitoring metrics

### Infrastructure
- **Kubernetes** - Container orchestration
- **RabbitMQ** - Message broker
- **Prometheus + Grafana** - Monitoring
- **Jaeger** - Distributed tracing

### Environment
System runs in Docker containers with support for:
- **Cloud**: AWS, GCP, Azure (Kubernetes)
- **On-premise**: Docker Compose, Kubernetes
- **Development**: Local Docker setup

## Project Structure

**Layered Architecture** (Layers → Containers → Components):

```
├── README.md                        <- Project overview and quick start
├── IMPLEMENTATION_SUMMARY.md        <- Architecture implementation details
├── PROJECT_STRUCTURE.md            <- Complete structural guide
├── docker-compose.yml              <- Development environment setup
│
├── docs/                           <- Complete system documentation
│   ├── README.docs.md             <- Documentation navigation guide
│   ├── architecture/              <- System architecture (C4 Model)
│   │   ├── c1-context.md         <- C4-1: System context
│   │   ├── c2-containers.md      <- C4-2: Containers and services
│   │   ├── c3-components.md      <- C4-3: Components and APIs
│   │   └── layers/               <- Layer-specific documentation
│   │       ├── presentation-layer.md      <- Presentation layer details
│   │       └── business-logic-layer.md    <- Business logic layer details
│   ├── design/                    <- Architectural decisions
│   │   ├── design-decisions.md    <- General ADRs
│   │   └── adr-001-layered-architecture.md <- Layered architecture ADR
│   ├── requirements/              <- Business analysis
│   ├── operations/                <- Deployment and monitoring
│   ├── methodology/               <- Research methodologies
│   └── user-guides/               <- Usage instructions
│
├── src/                           <- Layered architecture implementation
│   ├── presentation-layer/        <- User interfaces and API gateways
│   │   ├── web-ui/               <- Bootstrap web frontend
│   │   │   ├── components/       <- UI components (ExperimentDesigner, Dashboard, etc.)
│   │   │   ├── shared/           <- Frontend utilities and configuration
│   │   │   ├── index.html        <- Main HTML file
│   │   │   ├── Dockerfile        <- Container configuration
│   │   │   └── nginx.conf        <- Web server config
│   │   └── api-gateway/          <- FastAPI API gateway
│   │       ├── components/       <- Gateway components (auth, routing)
│   │       ├── shared/           <- Gateway utilities and config
│   │       ├── main.py           <- FastAPI application
│   │       ├── Dockerfile        <- Container configuration
│   │       └── requirements.txt  <- Python dependencies
│   │
│   ├── business-logic-layer/      <- Core domain services
│   │   ├── experiment-orchestrator/      <- Experiment coordination
│   │   │   ├── components/       <- Config, planning, scheduling components
│   │   │   ├── shared/           <- Orchestrator utilities and models
│   │   │   └── main.py           <- Service entry point
│   │   ├── experiment-tracking/          <- Lifecycle management
│   │   │   ├── components/       <- Tracking API and lifecycle components
│   │   │   └── shared/           <- Tracking utilities
│   │   ├── metrics-analysis/             <- Statistical analysis
│   │   │   ├── components/       <- Metric calculation and testing
│   │   │   └── shared/           <- Analysis utilities
│   │   ├── algorithm-registry/           <- Algorithm catalog
│   │   │   ├── components/       <- Registry and version management
│   │   │   └── shared/           <- Registry utilities
│   │   ├── benchmark-definition/         <- Problem definitions
│   │   │   ├── components/       <- Benchmark repository and versioning
│   │   │   └── shared/           <- Benchmark utilities
│   │   ├── publication-service/          <- Research publications
│   │   │   ├── components/       <- Citation and reference management
│   │   │   └── shared/           <- Publication utilities
│   │   └── report-generator/             <- Automated reporting
│   │       ├── components/       <- Template engine and exporters
│   │       └── shared/           <- Report utilities
│   │
│   ├── execution-layer/           <- Runtime and execution services
│   │   └── worker-runtime/       <- HPO algorithm execution
│   │       ├── components/       <- Execution engine and job management
│   │       ├── shared/           <- Runtime utilities
│   │       └── main.py           <- Worker service entry point
│   │
│   ├── support-layer/             <- Cross-cutting services
│   │   ├── auth-service/         <- Authentication & authorization
│   │   │   ├── components/       <- Auth components (JWT, roles)
│   │   │   ├── shared/           <- Auth utilities and config
│   │   │   └── main.py           <- Auth service entry point
│   │   └── infrastructure/       <- Infrastructure & operations
│   │       ├── k8s/              <- Kubernetes deployment manifests
│   │       ├── monitoring/       <- Monitoring configurations
│   │       └── scripts/          <- Infrastructure automation scripts
│   │           ├── validate-architecture.py  <- Architecture validation runner
│   │           └── verify-structure.ps1      <- Structure verification script
│   │
│   ├── data-layer/               <- Data persistence layer
│   └── shared/                   <- Cross-layer utilities
│       └── dependency_injection.py      <- DI container system
│
├── tests/                        <- Comprehensive test suites
│   ├── integration/              <- Architecture validation tests
│   │   ├── test_layered_architecture.py  <- Structure compliance tests
│   │   └── test_performance.py           <- Performance and scalability tests
│   └── conftest.py               <- Test configuration and fixtures
│
├── src/                           <- Layered architecture implementation
│
└── papers/                       <- Research papers and references
```

## Installation and Setup

### Requirements
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Python** 3.9+ (for development and testing)
- **Git** for version control
- **8GB+ RAM** recommended for full stack

### Quick Start
```bash
# Clone repository
git clone https://github.com/jedrzejpolaczek/aviarium.corvidae.corvus_corone.git
cd aviarium.corvidae.corvus_corone

# Start all services
docker-compose up -d

# Validate architecture (optional)
python src/support-layer/infrastructure/scripts/validate-architecture.py

# Check service status
docker-compose ps
```

### Application Access
- **Web UI**: http://localhost:8080 - Main user interface (served by API Gateway)
- **API Gateway**: http://localhost:8080 - REST API endpoints and Web UI
- **API Documentation**: http://localhost:8080/docs - Interactive API docs
- **Monitoring Dashboard**: http://localhost:3001 - Grafana (admin/admin)
- **Message Queue**: http://localhost:15672 - RabbitMQ Management (admin/admin)

### Development Setup
```bash
# Install Python dependencies for testing
pip install pytest pytest-asyncio pytest-json-report psutil

# Run architecture validation tests
python scripts/validate-architecture.py

# Run performance tests
pytest tests/integration/test_performance.py -v
```

## Contributing

### How to contribute to the project
1. **Fork** the repository
2. **Create** a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Coding Standards
- **Python**: [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- **JavaScript**: ESLint + Prettier
- **Docker**: Best practices for multi-stage builds
- **Documentation**: Markdown with Mermaid diagrams

### Testing & Validation
```bash
# Architecture validation
python src/support-layer/infrastructure/scripts/validate-architecture.py

# Layer structure tests
pytest tests/integration/test_layered_architecture.py -v

# Performance tests
pytest tests/integration/test_performance.py -v

# Full test suite
pytest tests/ -v
```

### Architecture Validation
The project includes comprehensive validation:
- **Structure Compliance**: Layer and component organization
- **Dependency Rules**: Proper layer boundary enforcement  
- **Performance Testing**: Scalability characteristics validation
- **Documentation Sync**: Implementation matches documentation
python scripts/validate-architecture.py

# Layer structure tests
pytest tests/integration/test_layered_architecture.py -v

# Performance and scalability tests
pytest tests/integration/test_performance.py -v

# Full test suite
```bash
pytest tests/ -v
```

### Architecture Validation
The project includes comprehensive validation of the layered architecture:
- **Structure Compliance**: Validates layer and component organization
- **Dependency Rules**: Ensures proper layer dependency boundaries
- **Performance Testing**: Validates scalability characteristics
- **Documentation Sync**: Checks implementation matches documentation

### Reporting Issues
- **Bugs**: Use GitHub Issues with bug report template
- **Feature requests**: GitHub Issues with feature request template
- **Questions**: GitHub Discussions

## License

This project is available under the MIT license. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project was made possible thanks to:
- **Research team** for concepts and requirements
- **HPO Community** for feedback and algorithms
- **Open Source** for tools and libraries

---

<!-- MARKDOWN LINKS & IMAGES -->
[ci-status-shield]: https://github.com/jedrzejpolaczek/aviarium.corvidae.corvus_corone/actions/workflows/main.yml/badge.svg?branch=main
