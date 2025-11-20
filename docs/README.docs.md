# Corvus Corone Documentation - Guide

> **HPO (Hyperparameter Optimization) Algorithm Benchmarking System**

Welcome to the Corvus Corone platform documentation! This guide will help you find the right information depending on your role and needs.

---

## 🚀 Quick start - where to begin?

### I'm new to the project
1. **Learn the requirements**: [Use Cases](requirements/use-cases.md)
2. **Start here**: [Architecture - System Context](architecture/c1-context.md)
3. **Understand the structure**: [Architecture - Containers](architecture/c2-containers.md)

### I'm a developer/architect
1. **System architecture**: [C4 - Context](architecture/c1-context.md) → [Containers](architecture/c2-containers.md) → [Components](architecture/c3-components.md)
2. **Design decisions**: [Design Decisions](design/design-decisions.md)
3. **Deployment**: [Deployment Guide](operations/deployment-guide.md)

### I'm a researcher/user
1. **What the system does**: [Use Cases](requirements/use-cases.md)
2. **Methodology**: [Benchmarking Practices](methodology/benchmarking-practices.md)
3. **Research workflow**: [Key Activities](user-guides/workflows.md)

### I'm an administrator/DevOps
1. **Deployment**: [Deployment Guide](operations/deployment-guide.md)
2. **Monitoring**: [Monitoring and Logging](operations/monitoring-guide.md)
3. **Container architecture**: [C4 - Containers](architecture/c2-containers.md)

---

## 📋 Complete Documentation Map

### 📋 Requirements & Analysis
| Document | Description | For whom |
|----------|-------------|----------|
| [Use Cases](requirements/use-cases.md) | Usage scenarios, actors, functional requirements | Product Owners, Analysts, Everyone |
| [Business Requirements](requirements/business-requirements.md) | Strategic goals, business value, stakeholder needs | Executives, Product Owners, Stakeholders |
| [Functional Requirements](requirements/functional-requirements.md) | Functional requirements (R1-R15) | Product Owners, Analysts, Developers |
| [Non-functional Requirements](requirements/non-functional-requirements.md) | Non-functional requirements (RNF1-RNF10) | Architects, DevOps, QA |
| [Requirements Traceability](requirements/requirements-traceability.md) | Requirements traceability matrix | Architects, PM, QA |

### 🏢 Architecture (C4 Model)
| Document | C4 Level | Description | For whom |
|----------|----------|-------------|----------|
| [Context](architecture/c1-context.md) | C4-1 | Users, external systems, requirements | Everyone |
| [Containers](architecture/c2-containers.md) | C4-2 | Applications, databases, communication | Developers, Architects |
| [Components](architecture/c3-components.md) | C4-3 | Modules, interfaces, technical details | Developers |

### 🔬 Methodology & Research
| Document | Description | For whom |
|----------|-------------|----------|
| [Benchmarking Practices](methodology/benchmarking-practices.md) | Research methodologies, comparison standards | Researchers, Data Scientists |

### 🛠️ Operations & Deployment
| Document | Description | For whom |
|----------|-------------|----------|
| [Deployment Guide](operations/deployment-guide.md) | PC vs Cloud, Docker, K8s, scaling | DevOps, Administrators |
| [Deployment Examples](operations/deployment-examples.md) | Detailed examples for each scenario | DevOps, Administrators |
| [Monitoring Guide](operations/monitoring-guide.md) | Logs, metrics, alerting, troubleshooting | DevOps, SRE |
| [Performance & SLA](operations/performance-sla.md) | Benchmarks, SLA definitions, KPIs | SRE, Management |

### 👥 User Guides
| Document | Description | For whom |
|----------|-------------|----------|
| [Workflows](user-guides/workflows.md) | Key activities, best practices | Researchers, Users |

### 🎨 Design & Decisions
| Document | Description | For whom |
|----------|-------------|----------|
| [Design Decisions](design/design-decisions.md) | **12 complete ADRs** - architectural justifications, trade-offs | Architects, Tech Leads |
| [Data Model](design/data-model.md) | Detailed data model (ERD) | Architects, Developers |

---

## ⭐ Key Documents (Production-Ready)

### For Decision Makers
- **[12 Architecture Decision Records](design/design-decisions.md)** - Complete justifications for all key technical decisions
- **[Performance & SLA Definitions](operations/performance-sla.md)** - Detailed benchmarks and service level agreements
- **[Requirements Traceability Matrix](requirements/requirements-traceability.md)** - Complete tracing requirements → architecture

### For Implementation Teams  
- **[Detailed Deployment Examples](operations/deployment-examples.md)** - Ready configurations for dev/staging/production
- **[Complete Architecture (C1-C2-C3-C4)](architecture/c1-context.md)** - Full C4 model with implementation
- **[Security & Monitoring Implementation](requirements/non-functional-requirements.md)** - RNF with concrete solutions

---

## 🔍 Find what you need

### Looking for information about...

**The system as a whole?**
→ [Context](architecture/c1-context.md)

**Specific services/containers?**
→ [Containers](architecture/c2-containers.md)

**HPO algorithm implementation?**
→ [Components - Algorithm SDK](architecture/c3-components.md#34-algorithm-sdk--plugin-runtime--komponenty)

**Jak uruchomić system?**
→ [Deployment Guide](operations/deployment-guide.md)

**Jak dodać nowy algorytm?**
→ [Use Cases UC3](requirements/use-cases.md) + [Algorithm SDK](architecture/c3-components.md#34-algorithm-sdk--plugin-runtime--komponenty)

**Jak porównać algorytmy?**
→ [Use Cases UC4](requirements/use-cases.md) + [Metrics Analysis](architecture/c3-components.md#36-metricsanalysisservice--komponenty)

**Dlaczego takie decyzje projektowe?**
→ [Design Decisions](design/design-decisions.md)

---

## 📋 Status dokumentacji

| Dokument | Status | Ostatnia aktualizacja |
|----------|--------|----------------------|
| Use Cases | ✅ Kompletny | 2025-11-19 |
| Functional Requirements | ✅ Kompletny | 2025-11-19 |
| Non-functional Requirements | ✅ Kompletny | 2025-11-19 |
| C4 Context | ✅ Kompletny | 2025-11-19 |
| C4 Containers | ✅ Kompletny | 2025-11-19 |
| C4 Components | ✅ Kompletny | 2025-11-19 |
| Benchmarking Practices | ✅ Kompletny | 2025-11-19 |
| Workflows | ✅ Kompletny | 2025-11-19 |
| Deployment Guide | ✅ Kompletny | 2025-11-19 |
| Monitoring Guide | ✅ Kompletny | 2025-11-19 |
| Design Decisions | ✅ Kompletny | 2025-11-19 |
| Data Model | ✅ Kompletny | 2025-11-19 |
| Requirements Traceability | ✅ Kompletny | 2025-11-19 |

---

## 🤝 Jak przyczynić się do dokumentacji

1. **Zgłoś błąd/propozycję**: Utwórz issue w repozytorium
2. **Zaproponuj zmianę**: Pull request z opisem
3. **Zadaj pytanie**: Skorzystaj z sekcji Discussions

**Zasady kontrybuowania**:
- Zachowaj struktur modelu C4 dla dokumentów architektury
- Używaj diagramów Mermaid dla wizualizacji
- Dodaj cross-reference do powiązanych dokumentów
- Aktualizuj tabelę statusu po zmianach

---

---

## 📚 Glossary of Key Terms

| Term | Definition |
|------|------------|
| **HPO** | Hyperparameter Optimization - hyperparameter optimization |
| **Benchmark** | Defined test problem for comparing algorithms |
| **Run** | Single execution of HPO algorithm on benchmark instance |
| **Plugin** | External HPO algorithm implemented as container |
| **Worker** | Execution unit running HPO algorithms |
| **Orchestrator** | Component managing experiment planning and execution |
| **Message Broker** | Task queuing system (RabbitMQ/Redis) |
| **ADR** | Architecture Decision Record - design decision justification |
| **C4 Model** | Context-Containers-Components-Code - architecture documentation methodology |
| **SDK** | Software Development Kit - tools for plugin developers |

---

**📝 Note**: This file was moved from `docs/README.md` to `docs/README.docs.md` to avoid conflicts with the main project README.

**↩️ Back to**: [Main Project README](../README.md)

---

*Ostatnia aktualizacja: 2025-11-20*