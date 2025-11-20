# Kontenery - Corvus Corone (C4-2)

> **Dekompozycja systemu HPO Benchmarking Platform na kontenery (aplikacje, usługi, bazy danych)**

---

## Diagram architektury kontenerów

```mermaid
---
config:
  look: neo
  layout: elk
  theme: redux-dark
---
flowchart TB
 subgraph Client["Client"]
        Ext["Zewnętrzne systemy AutoML / Analiza"]
  end
 subgraph PresentationLayer["PresentationLayer"]
        UI["Web UI / Frontend"]
        APIGW["API Gateway"]
  end
 subgraph BusinessLogicLayer["BusinessLogicLayer"]
        ORCH["Experiment Orchestrator Service"]
        TRK["Experiment Tracking Service"]
        ANALYTICS["MetricsAnalysisService"]
        BENCH["Benchmark Definition Service"]
        ALGREG["Algorithm Registry Service"]
        PUB["PublicationService"]
        RGS["ReportGeneratorService"]
  end
 subgraph ExecLayer["Warstwa wykonawcza"]
        MB["Message Broker"]
        WORKER["Worker Runtime / Execution Engine"]
        PLUGIN["Algorithm SDK / Plugin Runtime"]
  end
 subgraph Core["HPO Benchmarking Platform"]
        PresentationLayer
        BusinessLogicLayer
        ExecLayer
  end
 subgraph DataLayer["DataLayer"]
        DB[("Results Store - DB")]
        OBJ[("Object Storage")]
  end
 subgraph SupportLayer["SupportLayer"]
        AUTH["AuthService / Identity"]
        MON["Monitoring & Logging Stack"]
  end
    UI -- HTTP --> APIGW
    Ext -- HTTP API --> APIGW
    APIGW --> ORCH & TRK & ANALYTICS & BENCH & ALGREG & PUB & AUTH & RGS
    ORCH --> MB
    WORKER --> MB & TRK & BENCH & ALGREG & OBJ & PLUGIN
    RGS --> TRK & ANALYTICS & PUB & OBJ
    TRK --> DB
    BENCH --> DB
    ALGREG --> DB
    PUB --> DB
    Core --> MON
     DB:::Sky
     OBJ:::Sky
     AUTH:::Sky
     MON:::Sky
    classDef Sky stroke-width:1px, stroke-dasharray:none, stroke:#374D7C, fill:#E2EBFF, color:#374D7C
    style PresentationLayer stroke:#FFD600
    style BusinessLogicLayer stroke:#FF6D00
    style ExecLayer stroke:#00C853
    style Core stroke:#C8E6C9
    style Client stroke:#FFE0B2
    style SupportLayer stroke:#2962FF
    style DataLayer stroke:#AA00FF
    linkStyle 0 stroke:#FFD600,fill:none
    linkStyle 2 stroke:#FFD600,fill:none
    linkStyle 3 stroke:#FFD600,fill:none
    linkStyle 4 stroke:#FFD600,fill:none
    linkStyle 5 stroke:#FFD600,fill:none
    linkStyle 6 stroke:#FFD600,fill:none
    linkStyle 7 stroke:#FFD600,fill:none
    linkStyle 8 stroke:#FFD600,fill:none
    linkStyle 9 stroke:#FFD600,fill:none
    linkStyle 10 stroke:#FFD600,fill:none
    linkStyle 11 stroke:#00C853,fill:none
    linkStyle 12 stroke:#00C853,fill:none
    linkStyle 13 stroke:#00C853,fill:none
    linkStyle 14 stroke:#00C853,fill:none
    linkStyle 15 stroke:#00C853,fill:none
    linkStyle 16 stroke:#00C853,fill:none
    linkStyle 17 stroke:#D50000,fill:none
    linkStyle 18 stroke:#D50000,fill:none
    linkStyle 19 stroke:#D50000,fill:none
    linkStyle 20 stroke:#D50000,fill:none
    linkStyle 21 stroke:#AA00FF,fill:none
    linkStyle 22 stroke:#FF6D00,fill:none
    linkStyle 24 stroke:#2962FF,fill:none
```

---

## Przegląd kontenerów

### 🎨 Warstwa prezentacji
- **Web UI (Frontend)** - Interfejs użytkownika React/Vue/Angular
- **API Gateway** - Pojedynczy punkt wejścia HTTP/REST/GraphQL

### 🧠 Warstwa logiki biznesowej (Core Services)
- **Experiment Orchestrator** - Orkiestracja i planowanie eksperymentów
- **Experiment Tracking** - Śledzenie runów i metryk
- **MetricsAnalysisService** - Analiza i agregacja wyników
- **Benchmark Definition Service** - Definicje benchmarków i problemów
- **Algorithm Registry Service** - Katalog algorytmów HPO
- **PublicationService** - Zarządzanie publikacjami i referencjami
- **ReportGeneratorService** - Generowanie raportów

### ⚡ Warstwa wykonawcza
- **Worker Runtime** - Wykonywanie pojedynczych runów
- **Algorithm SDK/Plugin Runtime** - Uruchamianie pluginów algorytmów
- **Message Broker** - Kolejkowanie zadań i zdarzeń

### 💾 Warstwa danych
- **Results Store (Database)** - Relacyjna baza danych (PostgreSQL)
- **File/Object Storage** - Artefakty, datasety, modele

### 🔧 Warstwa wsparcia
- **Auth Service** - Autoryzacja i uwierzytelnianie
- **Monitoring & Logging** - Obserwowalność i diagnostyka

---

## Szczegółowy opis kontenerów

| Kontener | Warstwa | Odpowiedzialności | Komunikacja | PC vs Chmura | Rola w benchmarkingu |
|----------|---------|-------------------|-------------|--------------|---------------------|
| **Web UI (Frontend)** | **Prezentacji** | • Interfejs do definicji benchmarków i eksperymentów<br>• Podgląd katalogu algorytmów HPO<br>• Panel śledzenia eksperymentów<br>• Porównanie wyników<br>• Zarządzanie publikacjami<br>• Generowanie raportów<br>• Podstawowa administracja | • REST/GraphQL/WebSocket z **API Gateway** (sync) | **PC:** lokalny kontener lub pliki statyczne<br>**Chmura:** frontend (CDN/storage) | Prezentacja celów eksperymentu, konfiguracji, wyników i statystyk |
| **API Gateway / Backend API** | **Prezentacji** | • Pojedynczy punkt wejścia dla Web UI i systemów zewnętrznych<br>• Routing żądań do usług domenowych<br>• Autoryzacja/uwierzytelnianie<br>• Rate limiting, CORS | • Z klientami: HTTP REST/GraphQL (sync)<br>• Z usługami: HTTP/gRPC (sync) + Message Broker (async) | **PC:** jeden kontener (monolith/gateway)<br>**Chmura:** API Gateway + microservices | Centralny punkt integracji i udostępniania funkcji |
| **Experiment Orchestrator Service** | **Logiki biznesowej** | • Przyjmowanie definicji eksperymentów<br>• Walidacja planu (algorytmy, instancje)<br>• Tworzenie planu runów (algorytm × instancja × seed)<br>• Zlecanie runów workerom<br>• Zarządzanie stanem eksperymentu<br>• Kontrola reprodukowalności | • Sync: z API Gateway<br>• Async: do Worker Runtime (Message Broker)<br>• Events: RunCompleted/RunFailed | **PC:** jedna instancja<br>**Chmura:** skalowalny microservice, HA | Implementuje **plan eksperymentu** i kontrolę budżetu |
| **Worker Runtime / Execution Engine** | **Wykonawczej** | • Wykonywanie pojedynczych runów<br>• Ładowanie benchmarku i instancji<br>• Uruchamianie algorytmu HPO<br>• Raportowanie metryk<br>• Obsługa błędów i retry | • Async: odbiór zadań z Message Broker<br>• Sync/Async: zapisy do Tracking Service<br>• Dostęp do Object Storage | **PC:** 1-N workerów (docker-compose)<br>**Chmura:** worker pods, autoscaling | Zapewnia reprodukowalność i porównywalność runów |
| **Benchmark Definition Service** | **Logiki biznesowej** | • Przechowywanie definicji benchmarków<br>• Wersjonowanie benchmarków<br>• Listy datasetów, problemów<br>• Metryki, znane optimum/best-known | • Sync: API dla Orchestratora i Web UI | **PC/Chmura:** jeden kontener | Realizuje dobór instancji problemowych |
| **Algorithm Registry Service** | **Logiki biznesowej** | • Rejestr algorytmów HPO (wbudowane + pluginy)<br>• Metadane: nazwa, typ, parametry<br>• Wersjonowanie algorytmów<br>• Walidacja kompatybilności | • Sync: API dla Web UI, Orchestratora, Plugin Runtime | **PC/Chmura:** jeden kontener/usługa | Świadomy dobór algorytmów i konfiguracji |
| **Algorithm SDK / Plugin Runtime** | **Wykonawczej** | • Ładowanie i izolowanie pluginów<br>• Kontrakt API pluginu<br>• Walidacja wejść/wyjść<br>• Raportowanie wyników | • Lokalnie z Worker Runtime<br>• API lub wywołania językowe | **PC/Chmura:** ten sam kod, różne środowisko | Łatwe dodawanie algorytmów w ujednoliconym środowisku |
| **Experiment Tracking Service** | **Logiki biznesowej** | • API do logowania runów, metryk, tagów<br>• Powiązania: eksperyment→run→algorytm→benchmark<br>• Historia zmian parametrów<br>• Wyszukiwanie i filtrowanie | • Sync: API dla Worker Runtime, Orchestrator, Web UI | **PC:** 1 kontener<br>**Chmura:** skalowalny microservice | Panel śledzenia, analiza wyników, reprodukowalność |
| **MetricsAnalysisService** | **Logiki biznesowej** | • Agregowanie wyników<br>• Złożone metryki (czas do poziomu błędu)<br>• Testy statystyczne<br>• Wykresy porównawcze | • Sync: API dla Web UI<br>• Async: słuchanie zdarzeń RunCompleted | **PC:** 1 kontener<br>**Chmura:** skalowalny microservice | **Analiza i prezentacja wyników** benchmarków |
| **PublicationService** | **Logiki biznesowej** | • Katalog publikacji (DOI, BibTeX)<br>• Powiązania z algorytmami/benchmarkami<br>• Generowanie bibliografii<br>• Integracja z CrossRef/arXiv | • Sync: API dla Web UI, innych usług<br>• Sync/Async: wywołania do systemów bibliograficznych | **PC/Chmura:** usługa integracyjna | Łączy wyniki z literaturą naukową |
| **Results Store (Database)** | **Danych** | • Dane domenowe: Experiments, Runs, Metrics<br>• Algorithms, Benchmarks, Publications<br>• Powiązania i konfiguracje<br>• ACID transactions | • Internal: przez DAO z usług domenowych<br>• Orchestrator: tylko pośrednio przez API | **PC:** lokalny PostgreSQL<br>**Chmura:** zarządzana baza | Centralne repozytorium dla reprodukowalności |
| **Object Storage** | **Danych** | • Duże artefakty: datasety, modele<br>• Logi w plikach<br>• Wygenerowane raporty<br>• Versioning i lifecycle | • S3/API plikowe z workerów i usług | **PC:** lokalny dysk/MinIO<br>**Chmura:** S3/GCS/Azure Blob | Odtwarzalne przechowywanie artefaktów |
| **Message Broker (RabbitMQ/Redis)** | **Wykonawczej** | • Kolejka zadań runów<br>• Zdarzenia systemowe<br>• RunStarted/Completed/Failed<br>• ExperimentCompleted | • Async: komunikaty między usługami<br>• Pub/Sub pattern | **PC:** RabbitMQ (primary), Redis (fallback)<br>**Chmura:** Managed RabbitMQ lub Redis Streams | Elastyczny plan eksperymentu i skalowanie |
| **Monitoring & Logging Stack** | **Wsparcia** | • **Metrics:** Prometheus + Thanos (long-term)<br>• **Logging:** ELK Stack (Elasticsearch/Logstash/Kibana)<br>• **Tracing:** Jaeger distributed tracing<br>• **Dashboards:** Grafana unified visualization<br>• Business KPIs i SLA monitoring | • OpenTelemetry instrumentation<br>• Fluentd log shipping<br>• AlertManager notifications | **PC:** Prometheus+Grafana+basic logging<br>**Chmura:** Full observability stack z clustering | Three pillars observability (metrics/logs/traces) |
| **Auth Service** | **Wsparcia** | • OAuth2/OIDC authentication<br>• RBAC z role hierarchy (admin/plugin-author/researcher/viewer)<br>• JWT token management (15min TTL)<br>• MFA dla privileged operations<br>• API keys dla programmatic access | • Sync: OAuth2 flows, token validation<br>• Integration z external IdP | **PC:** built-in IdP z local accounts<br>**Chmura:** SAML/OIDC integration | Multi-tenant access control i compliance |
| **ReportGeneratorService** | **Logiki biznesowej** | • Raporty HTML/PDF/LaTeX<br>• Agregacja danych z wielu źródeł<br>• Templates i styling<br>• Bibliografia i cytowania | • Sync: API z Web UI i Orchestratora<br>• Data fetch z Tracking/Results Store | **PC/Chmura:** Python/Node.js serwis | Spójne, powtarzalne raporty benchmarków |

---

## Wzorce komunikacji

### 🔄 Synchroniczna (Request/Response)
- **Web UI ↔ API Gateway**: REST/GraphQL
- **API Gateway ↔ Core Services**: HTTP/gRPC
- **Worker ↔ Tracking Service**: REST API
- **Services ↔ Results Store**: Database queries

### ⚡ Asynchroniczna (Event-driven)
- **Orchestrator → Workers**: Task queue (RabbitMQ primary, Redis fallback)
- **Workers → Analytics**: RunCompleted events
- **System events**: ExperimentStarted/Completed/Failed (via Event Bus)
- **Notifications**: Alerts, status updates

### 📊 Batch Processing
- **Metrics aggregation**: Scheduled batch jobs
- **Report generation**: On-demand/scheduled
- **Data export**: Bulk operations



---

## Skalowanie i dostępność

### 📈 Strategie skalowania

| Warstwa | PC | Cloud | Bottlenecks |
|---------|-------|-------|-------------|
| **Frontend** | 1 instancja | CDN + multiple replicas | N/A (stateless) |
| **API Gateway** | 1 kontener | Load balancer + replicas | Rate limiting |
| **Core Services** | 1 każdy | Auto-scaling groups | Database connections |
| **Workers** | 1-N kontenerów | HPA based on queue length | CPU/Memory intensive |
| **Database** | Single instance | Read replicas, sharding | Concurrent writes |
| **Object Storage** | Local disk/MinIO | Distributed storage | Network I/O |

### 🛡️ Wysokiej dostępności (HA)

**Krytyczne komponenty:**
- **Results Store**: Master-slave replication
- **Message Broker**: Clustered setup
- **API Gateway**: Load balancing
- **Workers**: Stateless, easy replacement

**Recovery strategies:**
- **Database**: Point-in-time recovery, backups
- **Object Storage**: Cross-region replication
- **Services**: Health checks, auto-restart
- **Workers**: Retry policies, dead letter queues

---

## Monitoring kontenerów

### 📊 Key Metrics
- **Performance**: CPU, Memory, Network, Disk I/O
- **Business**: Run duration, success/failure rates
- **System**: Queue lengths, connection pools
- **Custom**: Algorithm-specific metrics

### 🚨 Alerting
- **Infrastructure**: Container down, resource exhaustion
- **Application**: High error rates, long-running jobs
- **Business**: Experiment failures, data quality issues

### 📈 Dashboards
- **System overview**: All containers health
- **Experiment tracking**: Active runs, queue status
- **Performance**: Latency, throughput per service
- **Business**: Benchmark results, algorithm comparisons

---

## Powiązane dokumenty

- **Poprzedni poziom**: [Kontekst (C4-1)](c1-context.md)
- **Następny poziom**: [Komponenty (C4-3)](c3-components.md)
- **Szczegóły implementacji**: [Kod (C4-4)](c4-code.md)
- **Wymagania**: [Functional Requirements](../requirements/functional-requirements.md), [Use Cases](../requirements/use-cases.md)
- **Deployment**: [Deployment Guide](../operations/deployment-guide.md)
- **Monitoring**: [Monitoring Guide](../operations/monitoring-guide.md)
