# Dokumentacja Corvus Corone - Przewodnik

> **System benchmarkowania algorytmów HPO (Hyperparameter Optimization)**

Witaj w dokumentacji platformy Corvus Corone! Ten przewodnik pomoże Ci znaleźć właściwe informacje w zależności od Twojej roli i potrzeb.

---

## 🚀 Szybki start - gdzie zacząć?

### Jestem nowy w projekcie
1. **Poznaj wymagania**: [Przypadki użycia](requirements/use-cases.md)
2. **Zacznij tutaj**: [Architektura - Kontekst systemu](architecture/c1-context.md)
3. **Zrozum strukturę**: [Architektura - Kontenery](architecture/c2-containers.md)

### Jestem programistą/architektem
1. **Architektura systemu**: [C4 - Kontekst](architecture/c1-context.md) → [Kontenery](architecture/c2-containers.md) → [Komponenty](architecture/c3-components.md)
2. **Decyzje projektowe**: [Design Decisions](design/design-decisions.md)
3. **Deployment**: [Przewodnik wdrożenia](operations/deployment-guide.md)

### Jestem badaczem/użytkownikiem
1. **Co system robi**: [Przypadki użycia](requirements/use-cases.md)
2. **Metodologia**: [Benchmarking Practices](methodology/benchmarking-practices.md)
3. **Workflow badawczy**: [Kluczowe aktywności](user-guides/workflows.md)

### Jestem administratorem/DevOps
1. **Deployment**: [Przewodnik wdrożenia](operations/deployment-guide.md)
2. **Monitoring**: [Monitoring i Logging](operations/monitoring-guide.md)
3. **Architektura kontenerów**: [C4 - Kontenery](architecture/c2-containers.md)

---

## 📚 Kompletna mapa dokumentacji

### 📋 Requirements & Analysis
| Dokument | Opis | Dla kogo |
|----------|------|----------|
| [Use Cases](requirements/use-cases.md) | Scenariusze użycia, aktorzy, wymagania funkcjonalne | Product Owners, Analitycy, Wszyscy |
| [Functional Requirements](requirements/functional-requirements.md) | Wymagania funkcjonalne (R1-R15) | Product Owners, Analitycy, Deweloperzy |
| [Non-functional Requirements](requirements/non-functional-requirements.md) | Wymagania niefunkcjonalne (RNF1-RNF10) | Architekci, DevOps, QA |
| [Requirements Traceability](requirements/requirements-traceability.md) | Macierz śledzenia wymagań | Architekci, PM, QA |

### 🏗️ Architektura (Model C4)
| Dokument | Poziom C4 | Opis | Dla kogo |
|----------|-----------|------|----------|
| [Context](architecture/c1-context.md) | C4-1 | Użytkownicy, systemy zewnętrzne, wymagania | Wszyscy |
| [Containers](architecture/c2-containers.md) | C4-2 | Aplikacje, bazy danych, komunikacja | Programiści, Architekci |
| [Components](architecture/c3-components.md) | C4-3 | Moduły, interfejsy, szczegóły techniczne | Programiści |

### 🔬 Methodology & Research
| Dokument | Opis | Dla kogo |
|----------|------|----------|
| [Benchmarking Practices](methodology/benchmarking-practices.md) | Metodologie badawcze, standardy porównań | Badacze, Data Scientists |

### 🛠️ Operations & Deployment
| Dokument | Opis | Dla kogo |
|----------|------|----------|
| [Deployment Guide](operations/deployment-guide.md) | PC vs Cloud, Docker, K8s, skalowanie | DevOps, Administratorzy |
| [Deployment Examples](operations/deployment-examples.md) | Szczegółowe przykłady dla każdego scenariusza | DevOps, Administratorzy |
| [Monitoring Guide](operations/monitoring-guide.md) | Logi, metryki, alertowanie, troubleshooting | DevOps, SRE |
| [Performance & SLA](operations/performance-sla.md) | Benchmarks, SLA definitions, KPIs | SRE, Management |

### 👥 User Guides
| Dokument | Opis | Dla kogo |
|----------|------|----------|
| [Workflows](user-guides/workflows.md) | Kluczowe aktywności, best practices | Badacze, Użytkownicy |

### 🎨 Design & Decisions
| Dokument | Opis | Dla kogo |
|----------|------|----------|
| [Design Decisions](design/design-decisions.md) | **12 kompletnych ADR** - uzasadnienia architekturalne, trade-offs | Architekci, Tech Leads |
| [Data Model](design/data-model.md) | Szczegółowy model danych (ERD) | Architekci, Deweloperzy |

---

## ⭐ Kluczowe dokumenty (Production-Ready)

### Dla Decision Makers
- **[12 Architecture Decision Records](design/design-decisions.md)** - Kompletne uzasadnienia wszystkich kluczowych decyzji technicznych
- **[Performance & SLA Definitions](operations/performance-sla.md)** - Szczegółowe benchmarks i service level agreements
- **[Requirements Traceability Matrix](requirements/requirements-traceability.md)** - Pełna śledzącać wymagania → architektura

### Dla Implementation Teams  
- **[Detailed Deployment Examples](operations/deployment-examples.md)** - Gotowe konfiguracje dla dev/staging/production
- **[Complete Architecture (C1-C2-C3-C4)](architecture/c1-context.md)** - Pełny model C4 z implementacją
- **[Security & Monitoring Implementation](requirements/non-functional-requirements.md)** - RNF z konkretnymi rozwiązaniami

---

## 🔍 Znajdź co potrzebujesz

### Szukasz informacji o...

**Systemie jako całości?**
→ [Context](architecture/c1-context.md)

**Konkretnych usługach/kontenerach?**
→ [Containers](architecture/c2-containers.md)

**Implementacji algorytmów HPO?**
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

## 📖 Glossary kluczowych terminów

| Termin | Definicja |
|--------|-----------|
| **HPO** | Hyperparameter Optimization - optymalizacja hiperparametrów |
| **Benchmark** | Zdefiniowany problem testowy do porównywania algorytmów |
| **Run** | Pojedyncze wykonanie algorytmu HPO na instancji benchmarku |
| **Plugin** | Zewnętrzny algorytm HPO zaimplementowany jako kontener |
| **Worker** | Jednostka wykonawcza uruchamiająca algorytmy HPO |
| **Orchestrator** | Komponent zarządzający planowaniem i wykonaniem eksperymentów |
| **Message Broker** | System kolejkowania zadań (RabbitMQ/Redis) |
| **ADR** | Architecture Decision Record - uzasadnienie decyzji projektowych |
| **C4 Model** | Context-Containers-Components-Code - metodyka dokumentacji architektury |
| **SDK** | Software Development Kit - narzędzia dla twórców pluginów |

---

**📝 Uwaga**: Ten plik został przeniesiony z `docs/README.md` na `docs/README.docs.md` aby uniknąć konfliktów z głównym README projektu.

**↩️ Powrót do**: [Główny README projektu](../README.md)

---

*Ostatnia aktualizacja: 2025-11-20*