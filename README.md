# Corvus Corone - HPO Benchmarking Platform

Platforma do benchmarkingu algorytmów hyperparameter optimization (HPO) z naciskiem na reproducibility i statistical rigor.

## 📖 Dokumentacja

**Production-ready dokumentacja** systemu została zorganizowana w strukturę łatwą w nawigacji:

**▶️ [Zacznij tutaj - Przewodnik po dokumentacji](docs/README.docs.md)**

**🎯 Kompletna dokumentacja obejmuje:**
- **Requirements**: Use cases, wymagania funkcjonalne i niefunkcjonalne + Requirements Traceability Matrix
- **Architektura**: Pełny model C4 (Context, Containers, Components, Code) 
- **Design Decisions**: **12 kompletnych ADR** pokrywających wszystkie kluczowe decyzje architekturalne
- **Operations**: Deployment examples, monitoring, **performance benchmarks & SLA definitions**
- **Methodology**: Benchmarking practices, metodologie badawcze
- **User Guides**: Workflows, instrukcje użytkowania

### 🎯 Szybkie linki:
- [Przypadki użycia](docs/requirements/use-cases.md) - Wymagania i scenariusze
- [Metodologie](docs/methodology/benchmarking-practices.md) - Praktyki badawcze
- [Architektura systemu](docs/architecture/c1-context.md) - Przegląd techniczny (Model C4)
- [Przewodnik wdrożenia](docs/operations/deployment-guide.md) - PC-first, Cloud-ready deployment
- [Requirements Traceability](docs/requirements/requirements-traceability.md) - Macierz śledzenia wymagań

---

*Szczegółowa nawigacja i opis wszystkich dokumentów: [docs/README.docs.md](docs/README.docs.md)*

## Project Data

**Project name:** Corvus Corone  
**Application name:** HPO Benchmarking Platform  
**Software version:** 1.0.0  
**Repository Purpose:** Hyperparameter Optimization algorithms benchmarking and comparison platform

## Spis treści

1. [Dokumentacja](#-dokumentacja)
2. [Project Data](#project-data)
3. [Architektura systemu](#-architektura-systemu)
4. [Technologie](#-technologie)
5. [Struktura projektu](#-struktura-projektu)
6. [Instalacja i uruchomienie](#-instalacja-i-uruchomienie)
7. [Wkład w rozwój](#-wkład-w-rozwój)
8. [Licencja](#-licencja)

## 🏗️ Architektura systemu

Corvus Corone to platforma mikrousługowa zaprojektowana dla benchmarkingu algorytmów HPO:

- **Mikrousługi**: API Gateway, Worker Pool, Experiment Tracking, Algorithm Registry + Plugin Runtime
- **Container orchestration**: Kubernetes dla skalowania
- **Message broker**: RabbitMQ (primary) / Redis (fallback) dla asynchronicznej komunikacji
- **Storage**: PostgreSQL (Results Store), Object Storage (artefakty), Redis (cache)
- **Monitoring**: Prometheus + Grafana, distributed tracing (patrz [Monitoring Stack](docs/operations/monitoring-guide.md))

Szczegóły w [dokumentacji architektury](docs/architecture/c1-context.md).

## 💻 Technologie

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
System działa w kontenerach Docker z obsługą:
- **Cloud**: AWS, GCP, Azure (Kubernetes)
- **On-premise**: Docker Compose, Kubernetes
- **Development**: Local Docker setup

## 📁 Struktura projektu

```
├── README.md                     <- Ten plik - główny opis projektu
├── docs/                         <- Kompletna dokumentacja systemu
│   ├── README.docs.md           <- Przewodnik po dokumentacji
│   ├── requirements/            <- Wymagania i analiza biznesowa
│   │   ├── use-cases.md        <- Przypadki użycia
│   │   └── non-functional-requirements.md <- Wymagania niefunkcjonalne
│   ├── architecture/            <- Architektura systemu (Model C4)
│   │   ├── c1-context.md       <- C4-1: Kontekst systemu
│   │   ├── c2-containers.md    <- C4-2: Kontenery i usługi
│   │   └── c3-components.md    <- C4-3: Komponenty i API
│   ├── methodology/             <- Metodologie badawcze
│   │   └── benchmarking-practices.md <- Praktyki benchmarkingu
│   ├── user-guides/             <- Przewodniki użytkownika
│   │   └── workflows.md        <- Procesy i workflow
│   ├── operations/              <- Dokumentacja operacyjna
│   │   ├── deployment-guide.md <- Przewodnik wdrożenia
│   │   └── monitoring-guide.md <- Monitoring i alerting
│   └── design/                  <- Decyzje projektowe
│       └── design-decisions.md  <- Architectural Decision Records
│
├── src/                         <- Kod źródłowy aplikacji
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
## 🚀 Instalacja i uruchomienie

### Wymagania
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Python** 3.9+ (dla development)
- **Kubernetes** 1.21+ (dla production)

### Szybki start (Docker Compose)
```bash
# Sklonuj repozytorium
git clone https://github.com/jedrzejpolaczek/aviarium.corvidae.corvus_corone.git
cd aviarium.corvidae.corvus_corone

# Uruchom system
docker-compose up -d

# Sprawdź status
docker-compose ps
```

### Dostęp do aplikacji
- **Web UI**: http://localhost:3000
- **API Gateway**: http://localhost:8080
- **Monitoring**: http://localhost:3001 (Grafana)

### Szczegółowe instrukcje
Pełny przewodnik instalacji: [Deployment Guide](docs/operations/deployment-guide.md)

## 🤝 Wkład w rozwój

### Jak przyczynić się do projektu
1. **Fork** repozytorium
2. **Utwórz** branch dla swojej funkcjonalności (`git checkout -b feature/AmazingFeature`)
3. **Commit** swoje zmiany (`git commit -m 'Add some AmazingFeature'`)
4. **Push** do brancha (`git push origin feature/AmazingFeature`)
5. **Otwórz** Pull Request

### Standardy kodowania
- **Python**: [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- **JavaScript**: ESLint + Prettier
- **Docker**: Best practices dla multi-stage builds
- **Dokumentacja**: Markdown z diagramami Mermaid

### Testing
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# E2E tests
pytest tests/e2e/
```

### Zgłaszanie problemów
- **Bugs**: Użyj GitHub Issues z template'em bug report
- **Feature requests**: GitHub Issues z template'em feature request
- **Pytania**: GitHub Discussions

## 📄 Licencja

Ten projekt jest dostępny na licencji MIT. Zobacz plik [LICENSE](LICENSE) po szczegóły.

## 🏆 Podziękowania

Projekt powstał dzięki:
- **Zespołowi badawczemu** za koncepcje i wymagania
- **Community HPO** za feedback i algorytmy
- **Open Source** za narzędzia i biblioteki

---

**Corvus Corone** - Advancing HPO research through reproducible benchmarking 🚀

<!-- MARKDOWN LINKS & IMAGES -->
[ci-status-shield]: https://github.com/jedrzejpolaczek/aviarium.corvidae.corvus_corone/actions/workflows/main.yml/badge.svg?branch=main
