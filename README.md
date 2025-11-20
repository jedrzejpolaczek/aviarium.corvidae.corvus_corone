# Corvus Corone - HPO Benchmarking Platform

Platform for benchmarking hyperparameter optimization (HPO) algorithms with emphasis on reproducibility and statistical rigor.

## 📖 Documentation

**Production-ready documentation** of the system has been organized into an easy-to-navigate structure:

**▶️ [Start here - Documentation Guide](docs/README.docs.md)**

**🎯 Complete documentation includes:**
- **Requirements**: Use cases, functional and non-functional requirements + Requirements Traceability Matrix
- **Architecture**: Full C4 model (Context, Containers, Components, Code) 
- **Design Decisions**: **12 complete ADRs** covering all key architectural decisions
- **Operations**: Deployment examples, monitoring, **performance benchmarks & SLA definitions**
- **Methodology**: Benchmarking practices, research methodologies
- **User Guides**: Workflows, usage instructions

### 🎯 Quick links:
- [Use Cases](docs/requirements/use-cases.md) - Requirements and scenarios
- [Methodologies](docs/methodology/benchmarking-practices.md) - Research practices
- [System Architecture](docs/architecture/c1-context.md) - Technical overview (C4 Model)
- [Deployment Guide](docs/operations/deployment-guide.md) - PC-first, Cloud-ready deployment
- [Requirements Traceability](docs/requirements/requirements-traceability.md) - Requirements traceability matrix

---

*Detailed navigation and description of all documents: [docs/README.docs.md](docs/README.docs.md)*

## Project Data

**Project name:** Corvus Corone  
**Application name:** HPO Benchmarking Platform  
**Software version:** 1.0.0  
**Repository Purpose:** Hyperparameter Optimization algorithms benchmarking and comparison platform

## Table of Contents

1. [Documentation](#-documentation)
2. [Project Data](#project-data)
3. [System Architecture](#-system-architecture)
4. [Technologies](#-technologies)
5. [Project Structure](#-project-structure)
6. [Installation and Setup](#-installation-and-setup)
7. [Contributing](#-contributing)
8. [License](#-license)

## 🏗️ System Architecture

Corvus Corone is a microservices platform designed for benchmarking HPO algorithms:

- **Microservices**: API Gateway, Worker Pool, Experiment Tracking, Algorithm Registry + Plugin Runtime
- **Container orchestration**: Kubernetes for scaling
- **Message broker**: RabbitMQ (primary) / Redis (fallback) for asynchronous communication
- **Storage**: PostgreSQL (Results Store), Object Storage (artifacts), Redis (cache)
- **Monitoring**: Prometheus + Grafana, distributed tracing (see [Monitoring Stack](docs/operations/monitoring-guide.md))

Details in [architecture documentation](docs/architecture/c1-context.md).

## 💻 Technologies

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

## 📁 Project Structure

```
├── README.md                     <- This file - main project description
├── docs/                         <- Complete system documentation
│   ├── README.docs.md           <- Documentation guide
│   ├── requirements/            <- Requirements and business analysis
│   │   ├── use-cases.md        <- Use cases
│   │   └── non-functional-requirements.md <- Non-functional requirements
│   ├── architecture/            <- System architecture (C4 Model)
│   │   ├── c1-context.md       <- C4-1: System context
│   │   ├── c2-containers.md    <- C4-2: Containers and services
│   │   └── c3-components.md    <- C4-3: Components and APIs
│   ├── methodology/             <- Research methodologies
│   │   └── benchmarking-practices.md <- Benchmarking practices
│   ├── user-guides/             <- User guides
│   │   └── workflows.md        <- Processes and workflows
│   ├── operations/              <- Operational documentation
│   │   ├── deployment-guide.md <- Deployment guide
│   │   └── monitoring-guide.md <- Monitoring and alerting
│   └── design/                  <- Design decisions
│       └── design-decisions.md  <- Architectural Decision Records
│
├── src/                         <- Application source code
│   ├── api-gateway/            <- API Gateway service
│   ├── orchestrator/           <- Experiment Orchestrator
│   ├── worker/                 <- Worker Pool
│   ├── tracking/               <- Experiment Tracking service
│   ├── plugin-manager/         <- Plugin Manager
│   ├── report-generator/       <- Report Generator
│   └── web-ui/                 <- Web User Interface
│
├── deploy/                      <- Deployment configurations
│   ├── docker/                 <- Docker configurations
│   ├── kubernetes/             <- Kubernetes manifests
│   └── compose/                <- Docker Compose files
│
├── tests/                       <- Test suites
├── scripts/                     <- Utility scripts
└── examples/                    <- Example algorithms and benchmarks
```
## 🚀 Installation and Run

### Requirements
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Python** 3.9+ (dla development)
- **Kubernetes** 1.21+ (dla production)

### Quick start (Docker Compose)
```bash
# Clone repository
git clone https://github.com/jedrzejpolaczek/aviarium.corvidae.corvus_corone.git
cd aviarium.corvidae.corvus_corone

# Run system
docker-compose up -d

# Check status
docker-compose ps
```

### App access
- **Web UI**: http://localhost:3000
- **API Gateway**: http://localhost:8080
- **Monitoring**: http://localhost:3001 (Grafana)

### Detailed Instructions
Complete installation guide: [Deployment Guide](docs/operations/deployment-guide.md)

## 🤝 Contributing

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

### Testing
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# E2E tests
pytest tests/e2e/
```

### Reporting Issues
- **Bugs**: Use GitHub Issues with bug report template
- **Feature requests**: GitHub Issues with feature request template
- **Questions**: GitHub Discussions

## 📄 License

This project is available under the MIT license. See the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

This project was made possible thanks to:
- **Research team** for concepts and requirements
- **HPO Community** for feedback and algorithms
- **Open Source** for tools and libraries

---

**Corvus Corone** - Advancing HPO research through reproducible benchmarking 🚀

<!-- MARKDOWN LINKS & IMAGES -->
[ci-status-shield]: https://github.com/jedrzejpolaczek/aviarium.corvidae.corvus_corone/actions/workflows/main.yml/badge.svg?branch=main
