# Requirements Traceability Matrix

> **Document**: Requirements traceability matrix - relationships between requirements and use cases  
> **Version**: 1.0  
> **Date**: 2025-11-19  
> **Status**: ✅ Complete

## 1. Introduction

This document presents the complete Requirements Traceability Matrix (RTM) for the Corvus Corone system, showing relationships between:
- **Business requirements (BG1-BG6)**
- **Functional requirements (R1-R15)**
- **Non-functional requirements (RNF1-RNF10)**  
- **Use cases (UC1-UC9)**
- **Architecture components**

## 2. Business Requirements Alignment

| Business Requirement | Related Functional Requirements | Related Non-Functional Requirements | Implementation Priority |
|---------------------|--------------------------------|-------------------------------------|------------------------|
| **BR1 - Reproducible Research Support** | R3, R9, R11, R14 | RNF2, RNF6, RNF8 | High |
| **BR2 - Collaborative Research Environment** | R7, R10, R12 | RNF3, RNF5, RNF8 | Medium |
| **BR3 - Methodological Rigor** | R8, R9, R11 | RNF6, RNF8, RNF10 | High |
| **BR4 - Production Readiness Assessment** | R1, R5, R8, R15 | RNF1, RNF2, RNF10 | High |
| **BR5 - Decision Support System** | R1, R4, R8, R14 | RNF4, RNF10 | Medium |
| **BR6 - Enterprise Integration** | R12, R15 | RNF3, RNF5, RNF9 | Medium |
| **BR7 - Developer Experience** | R2, R12, R13 | RNF5, RNF8 | High |
| **BR8 - Content Management** | R1, R3, R4, R10 | RNF2, RNF3, RNF6 | Medium |
| **BR9 - Platform Operations** | R6, R7, R15 | RNF1, RNF2, RNF4, RNF7, RNF9, RNF10 | High |

## 3. Functional Requirements - UC Mapping

### 3.1. Mapping Table R1-R15 → UC1-UC9

| Requirement | Description | UC1 | UC2 | UC3 | UC4 | UC5 | UC6 | UC7 | UC8 | UC9 |
|-----------|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| **R1** - HPO Algorithm Catalog (built-in) | Storage and cataloging of built-in algorithms | ⭐ | ✅ | - | ✅ | ✅ | - | - | - | ✅ |
| **R2** - HPO Plugin Support | Support for external algorithms as plugins | ⭐ | ✅ | ⭐ | ✅ | ✅ | - | - | - | ✅ |
| **R3** - Algorithm Versioning | Version management of algorithms and plugins | ✅ | ✅ | ⭐ | ✅ | ✅ | - | - | - | ✅ |
| **R4** - Benchmark Catalog | Problem definitions, datasets, metrics | ⭐ | ⭐ | - | ✅ | ✅ | - | - | - | ✅ |
| **R5** - Experiment Configuration | Algorithm selection, instances, budgets | ⭐ | - | - | ✅ | ✅ | - | - | - | - |
| **R6** - Experiment Orchestration | Planning, queuing, retry | ⭐ | - | - | - | ✅ | - | ⭐ | ⭐ | - |
| **R7** - Tracking Panel | Experiment list, statuses, metrics | ✅ | - | ✅ | ✅ | ⭐ | - | ✅ | ✅ | - |
| **R8** - Results Comparison | Charts, statistics, statistical tests | - | - | - | ⭐ | ✅ | - | - | - | - |
| **R9** - Logs and Artifacts | Recording models, charts, configurations | ✅ | - | ✅ | ✅ | ⭐ | - | ✅ | ✅ | - |
| **R10** - Publication Management | Adding, editing, algorithm associations | - | - | ✅ | ✅ | - | ⭐ | - | - | ✅ |
| **R11** - Report Generation | Reports with bibliography and citations section | - | - | - | ✅ | - | ✅ | - | - | ⭐ |
| **R12** - Integration API | REST API for external systems | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | ⭐ |
| **R13** - Plugin SDK | API for creating custom HPO algorithms | - | - | ⭐ | - | - | - | - | - | ✅ |
| **R14** - Data Export | CSV/JSON/Parquet for analytical tools | - | - | - | ✅ | ✅ | - | - | - | ⭐ |
| **R15** - PC-first, cloud-ready deployment | PC mode and K8s | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐ | ⭐ | ✅ |

**Legend:**
- ⭐ = Key requirement for UC (primary coverage)
- ✅ = Important requirement (secondary coverage)
- - = Does not apply directly

### 3.2. Requirements Coverage by Use Cases

| Requirement | UC Coverage | Main UC | Coverage % |
|-----------|-------------|-----------|-------------|
| R1 | UC1, UC2, UC4, UC5, UC9 | UC1 | 55% |
| R2 | UC1, UC2, UC3, UC4, UC5, UC9 | UC1, UC3 | 66% |
| R3 | UC1, UC2, UC3, UC4, UC5, UC9 | UC3 | 66% |
| R4 | UC1, UC2, UC4, UC5, UC9 | UC1, UC2 | 55% |
| R5 | UC1, UC4, UC5 | UC1 | 33% |
| R6 | UC1, UC5, UC7, UC8 | UC1, UC7, UC8 | 44% |
| R7 | UC1, UC3, UC4, UC5, UC7, UC8 | UC5 | 66% |
| R8 | UC4, UC5 | UC4 | 22% |
| R9 | UC1, UC3, UC4, UC5, UC7, UC8 | UC5 | 66% |
| R10 | UC3, UC4, UC6, UC9 | UC6 | 44% |
| R11 | UC4, UC6, UC9 | UC9 | 33% |
| R12 | UC1-UC6, UC9 | UC9 | 77% |
| R13 | UC3, UC9 | UC3 | 22% |
| R14 | UC4, UC5, UC9 | UC9 | 33% |
| R15 | UC1-UC9 | UC7, UC8 | 100% |

## 4. Non-functional Requirements - UC Mapping

### 3.1. Mapping Table RNF1-RNF10 → UC1-UC9

| Requirement | UC1 | UC2 | UC3 | UC4 | UC5 | UC6 | UC7 | UC8 | UC9 | Key Components |
|-----------|-----|-----|-----|-----|-----|-----|-----|-----|-----|---------------------|
| **RNF1** - Scalability | ⭐ | ✅ | ✅ | ✅ | ✅ | - | ⭐ | ⭐ | ✅ | Worker Runtime, Message Broker |
| **RNF2** - Reliability | ⭐ | ✅ | ✅ | ✅ | ⭐ | ✅ | ⭐ | ⭐ | ✅ | Orchestrator, Experiment Tracking |
| **RNF3** - Security | ✅ | ✅ | ⭐ | ✅ | ✅ | ✅ | ⭐ | ⭐ | ⭐ | Auth Service, Plugin Runtime |
| **RNF4** - Observability | ✅ | ✅ | ✅ | ✅ | ⭐ | - | ⭐ | ⭐ | ✅ | Monitoring Stack, Tracking |
| **RNF5** - Extensibility | ⭐ | ✅ | ⭐ | ✅ | ✅ | - | ✅ | ✅ | ⭐ | Plugin Manager, Algorithm SDK |
| **RNF6** - Cloud-ready | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐ | ⭐ | ✅ | All containers |
| **RNF7** - Reproducibility | ⭐ | ✅ | ✅ | ✅ | ⭐ | - | ✅ | ✅ | ✅ | Environment Snapshots, Tracking |
| **RNF8** - Usability | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ✅ | ✅ | ⭐ | Web UI, API Gateway |
| **RNF9** - Backup/DR | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐ | ⭐ | ✅ | Results Store, Object Storage |
| **RNF10** - Performance | ⭐ | ✅ | ✅ | ⭐ | ⭐ | ✅ | ⭐ | ⭐ | ⭐ | Worker Runtime, API Gateway |

## 5. UC Coverage Analysis

### 5.1. Detailed Requirements Coverage by UC

#### UC1 - Configure and Run Benchmark Experiment
**Requirements Coverage**: R1⭐, R2⭐, R4⭐, R5⭐, R6⭐, R15✅ + all RNF
- **Key for**: Core system functionality
- **Components**: Orchestrator, Web UI, Algorithm Registry, Benchmark Definition

#### UC2 - Browse Benchmark Catalog  
**Requirements Coverage**: R1✅, R2✅, R4⭐, R15✅ + RNF1-2, RNF6, RNF8⭐
- **Key for**: Exploration of available benchmarks
- **Components**: Benchmark Definition Service, Web UI

#### UC3 - Register Custom HPO Algorithm
**Requirements Coverage**: R2⭐, R3⭐, R13⭐, R15✅ + RNF3⭐, RNF5⭐, RNF8⭐  
- **Key for**: System extensibility
- **Components**: Algorithm Registry, Plugin Runtime, Auth Service

#### UC4 - Compare Algorithm Results
**Requirements Coverage**: R8⭐, R11✅, R14✅ + RNF8⭐, RNF10⭐
- **Key for**: Benchmarking results analysis
- **Components**: MetricsAnalysisService, Web UI, Tracking

#### UC5 - Browse and Filter Experiments  
**Requirements Coverage**: R7⭐, R9⭐ + RNF2⭐, RNF4⭐, RNF7⭐, RNF8⭐, RNF10⭐
- **Key for**: Experiment history management  
- **Components**: Experiment Tracking, Web UI

#### UC6 - Manage Publication References
**Requirements Coverage**: R10⭐, R11✅ + RNF8⭐
- **Key for**: Scientific context of algorithms
- **Components**: Publication Service, Web UI

#### UC7 - Deploy System Locally (PC)
**Requirements Coverage**: R6⭐, R15⭐ + RNF1⭐, RNF2⭐, RNF3⭐, RNF4⭐, RNF6⭐, RNF9⭐, RNF10⭐
- **Key for**: PC-first deployment
- **Components**: All (docker-compose)

#### UC8 - Deploy System in Cloud (K8s)  
**Requirements Coverage**: R6⭐, R15⭐ + RNF1⭐, RNF2⭐, RNF3⭐, RNF4⭐, RNF6⭐, RNF9⭐, RNF10⭐
- **Key for**: Cloud deployment and scaling
- **Components**: All (Kubernetes)

#### UC9 - API Integration
**Requirements Coverage**: R12⭐, R14⭐, R11⭐ + RNF3⭐, RNF5⭐, RNF8⭐, RNF10⭐
- **Key for**: Programmatic access and integration
- **Components**: API Gateway, all services

### 4.2. Gap Analysis - Potential Gaps

| Area | Gap Description | Risk Level | Mitigation |
|------|-----------------|------------|------------|
| **R8 Coverage** | Only UC4+UC5 cover comparison | 🟡 Medium | UC4 is comprehensive for this requirement |
| **R13 Coverage** | SDK only in UC3+UC9 | 🟡 Medium | UC3 covers plugin development comprehensively |
| **R11 Coverage** | Reporting in UC4+UC6+UC9 | 🟢 Low | Distributed reporting is OK |
| **Performance Testing** | No dedicated UC for load testing | 🟡 Medium | Add UC10 - Performance Testing |

## 6. Architecture Components vs Requirements

### 5.1. Component vs Functional Requirements Matrix

| Component | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15 |
|-----------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|-----|
| **Web UI** | ✅ | ✅ | ✅ | ✅ | ⭐ | - | ⭐ | ⭐ | ✅ | ⭐ | ✅ | ✅ | - | ✅ | ✅ |
| **API Gateway** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐ | ✅ | ✅ | ⭐ |
| **Orchestrator** | ✅ | ✅ | ✅ | ✅ | ⭐ | ⭐ | ✅ | - | ✅ | - | - | ✅ | - | - | ⭐ |
| **Algorithm Registry** | ⭐ | ⭐ | ⭐ | - | ✅ | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐ | ✅ | ✅ |
| **Benchmark Definition** | - | - | - | ⭐ | ⭐ | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ | ✅ |
| **Worker Runtime** | ✅ | ⭐ | ✅ | ✅ | ✅ | ⭐ | ✅ | - | ⭐ | - | - | ✅ | ⭐ | - | ⭐ |
| **Experiment Tracking** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐ | ✅ | ⭐ | ✅ | ✅ | ⭐ | - | ⭐ | ✅ |
| **MetricsAnalysisService** | - | - | - | ✅ | - | - | ✅ | ⭐ | ✅ | - | ⭐ | ✅ | - | ⭐ | ✅ |
| **Publication Service** | ✅ | ✅ | ✅ | ✅ | - | - | - | - | ✅ | ⭐ | ⭐ | ✅ | - | ✅ | ✅ |
| **Plugin Runtime** | - | ⭐ | ⭐ | - | - | ✅ | ✅ | - | ✅ | - | - | ✅ | ⭐ | - | ✅ |

### 5.2. Components vs Non-functional Requirements

| Component | RNF1 | RNF2 | RNF3 | RNF4 | RNF5 | RNF6 | RNF7 | RNF8 | RNF9 | RNF10 |
|-----------|------|------|------|------|------|------|------|------|------|-------|
| **Web UI** | ✅ | ✅ | ✅ | ✅ | - | ✅ | - | ⭐ | - | ⭐ |
| **API Gateway** | ✅ | ✅ | ⭐ | ✅ | - | ✅ | - | ✅ | - | ⭐ |
| **Orchestrator** | ✅ | ⭐ | ✅ | ✅ | ✅ | ✅ | ⭐ | ✅ | ✅ | ✅ |
| **Worker Pool** | ⭐ | ✅ | ✅ | ✅ | ⭐ | ✅ | ⭐ | - | - | ⭐ |
| **Experiment Tracking** | ✅ | ✅ | ✅ | ⭐ | - | ✅ | ⭐ | ✅ | ⭐ | ✅ |
| **Plugin Manager** | - | ✅ | ⭐ | ✅ | ⭐ | ✅ | ⭐ | ✅ | ✅ | ✅ |
| **Results Store** | ✅ | ⭐ | ✅ | ✅ | - | ✅ | ⭐ | - | ⭐ | ✅ |
| **Object Storage** | ✅ | ✅ | ✅ | ✅ | - | ⭐ | ⭐ | - | ⭐ | ✅ |
| **Message Broker** | ⭐ | ⭐ | ✅ | ✅ | - | ✅ | - | - | ✅ | ⭐ |
| **Monitoring Stack** | ✅ | ✅ | ✅ | ⭐ | - | ✅ | ✅ | ✅ | ✅ | ⭐ |

## 7. Recommendations

### 6.1. Implementation Priorities

**Phase 1 - Core (UC1, UC2, UC7)**:
- Web UI, API Gateway, Orchestrator
- Algorithm Registry, Benchmark Definition  
- Basic deployment (docker-compose)

**Phase 2 - Extensions (UC3, UC5, UC6)**:
- Plugin Runtime, Algorithm SDK
- Experiment Tracking, Filtering
- Publication Service

**Phase 3 - Analytics (UC4, UC9)**:
- MetricsAnalysisService
- Advanced API, Export capabilities
- Reporting system

**Phase 4 - Scale (UC8)**:
- Kubernetes deployment
- Advanced monitoring, DR procedures
- Multi-tenant capabilities

### 6.2. Potential UC Extensions

- **UC10** - Performance benchmarking and load testing
- **UC11** - Multi-tenant organization management  
- **UC12** - Advanced alerting and notifications
- **UC13** - Batch experiment scheduling

## 8. Related Documents

- **Business Requirements**: [Business Requirements & Goals](business-requirements.md)
- **Functional Requirements**: [Functional Requirements](functional-requirements.md)
- **Non-functional Requirements**: [Non-functional Requirements](non-functional-requirements.md)
- **Use Cases**: [Use Cases](use-cases.md)
- **System Architecture**: [C4 Model - Context](../architecture/c1-context.md)
- **Design Decisions**: [Architecture Decision Records](../design/design-decisions.md)
- **Data Model**: [Data Model](../design/data-model.md)

## Cross-reference

- **Use Cases**: [Use Cases](use-cases.md)
- **Requirements**: [Business Requirements](business-requirements.md), [Functional Requirements](functional-requirements.md), [Non-functional Requirements](non-functional-requirements.md)
- **Architecture**: [C4 Components](../architecture/c3-components.md)
- **Data Model**: [Data Model](../design/data-model.md)
