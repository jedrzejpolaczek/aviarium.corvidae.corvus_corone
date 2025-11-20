# Requirements Traceability Matrix - Corvus Corone

> **Dokument**: Macierz śledzenia wymagań - powiązania między wymaganiami a przypadkami użycia  
> **Wersja**: 1.0  
> **Data**: 2025-11-19  
> **Status**: ✅ Complete

## 1. Wprowadzenie

Ten dokument przedstawia pełną macierz śledzenia wymagań (RTM - Requirements Traceability Matrix) dla systemu Corvus Corone, pokazując powiązania między:
- **Wymaganiami funkcjonalnymi (R1-R15)**
- **Wymaganiami niefunkcjonalnymi (RNF1-RNF10)**  
- **Przypadkami użycia (UC1-UC9)**
- **Komponentami architektury**

## 2. Wymagania funkcjonalne - mapowanie na UC

### 2.1. Tabela mapowania R1-R15 → UC1-UC9

| Wymaganie | Opis | UC1 | UC2 | UC3 | UC4 | UC5 | UC6 | UC7 | UC8 | UC9 |
|-----------|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| **R1** - Katalog algorytmów HPO (wbudowanych) | Przechowywanie i katalogowanie wbudowanych algorytmów | ⭐ | ✅ | - | ✅ | ✅ | - | - | - | ✅ |
| **R2** - Wsparcie dla pluginów HPO | Obsługa algorytmów zewnętrznych jako pluginy | ⭐ | ✅ | ⭐ | ✅ | ✅ | - | - | - | ✅ |
| **R3** - Wersjonowanie algorytmów | Zarządzanie wersjami algorytmów i pluginów | ✅ | ✅ | ⭐ | ✅ | ✅ | - | - | - | ✅ |
| **R4** - Katalog benchmarków | Definicje problemów, datasety, metryki | ⭐ | ⭐ | - | ✅ | ✅ | - | - | - | ✅ |
| **R5** - Konfiguracja eksperymentów | Dobór algorytmów, instancji, budżetów | ⭐ | - | - | ✅ | ✅ | - | - | - | - |
| **R6** - Orkiestracja eksperymentów | Planowanie, kolejkowanie, retry | ⭐ | - | - | - | ✅ | - | ⭐ | ⭐ | - |
| **R7** - Panel śledzenia | Lista eksperymentów, statusy, metryki | ✅ | - | ✅ | ✅ | ⭐ | - | ✅ | ✅ | - |
| **R8** - Porównywanie wyników | Wykresy, statystyki, testy statystyczne | - | - | - | ⭐ | ✅ | - | - | - | - |
| **R9** - Logi i artefakty | Rejestrowanie modeli, wykresów, konfiguracji | ✅ | - | ✅ | ✅ | ⭐ | - | ✅ | ✅ | - |
| **R10** - Zarządzanie publikacji | Dodawanie, edycja, powiązania z algorytmami | - | - | ✅ | ✅ | - | ⭐ | - | - | ✅ |
| **R11** - Generowanie raportów | Raporty z sekcją bibliografii i cytowań | - | - | - | ✅ | - | ✅ | - | - | ⭐ |
| **R12** - API integracyjne | REST API dla systemów zewnętrznych | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | ⭐ |
| **R13** - SDK pluginów | API do tworzenia własnych algorytmów HPO | - | - | ⭐ | - | - | - | - | - | ✅ |
| **R14** - Eksport danych | CSV/JSON/Parquet dla narzędzi analitycznych | - | - | - | ✅ | ✅ | - | - | - | ⭐ |
| **R15** - PC-first, cloud-ready deployment | Tryb PC i K8s | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐ | ⭐ | ✅ |

**Legenda:**
- ⭐ = Kluczowe wymaganie dla UC (primary coverage)
- ✅ = Ważne wymaganie (secondary coverage)
- - = Nie dotyczy bezpośrednio

### 2.2. Pokrycie wymagań przez przypadki użycia

| Wymaganie | Pokrycie UC | Główne UC | Coverage % |
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

## 3. Wymagania niefunkcjonalne - mapowanie na UC

### 3.1. Tabela mapowania RNF1-RNF10 → UC1-UC9

| Wymaganie | UC1 | UC2 | UC3 | UC4 | UC5 | UC6 | UC7 | UC8 | UC9 | Kluczowe komponenty |
|-----------|-----|-----|-----|-----|-----|-----|-----|-----|-----|---------------------|
| **RNF1** - Skalowalność | ⭐ | ✅ | ✅ | ✅ | ✅ | - | ⭐ | ⭐ | ✅ | Worker Runtime, Message Broker |
| **RNF2** - Niezawodność | ⭐ | ✅ | ✅ | ✅ | ⭐ | ✅ | ⭐ | ⭐ | ✅ | Orchestrator, Experiment Tracking |
| **RNF3** - Bezpieczeństwo | ✅ | ✅ | ⭐ | ✅ | ✅ | ✅ | ⭐ | ⭐ | ⭐ | Auth Service, Plugin Runtime |
| **RNF4** - Obserwowalność | ✅ | ✅ | ✅ | ✅ | ⭐ | - | ⭐ | ⭐ | ✅ | Monitoring Stack, Tracking |
| **RNF5** - Rozszerzalność | ⭐ | ✅ | ⭐ | ✅ | ✅ | - | ✅ | ✅ | ⭐ | Plugin Manager, Algorithm SDK |
| **RNF6** - Cloud-ready | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐ | ⭐ | ✅ | Wszystkie kontenery |
| **RNF7** - Reprodukowalność | ⭐ | ✅ | ✅ | ✅ | ⭐ | - | ✅ | ✅ | ✅ | Environment Snapshots, Tracking |
| **RNF8** - Użyteczność | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ✅ | ✅ | ⭐ | Web UI, API Gateway |
| **RNF9** - Backup/DR | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐ | ⭐ | ✅ | Results Store, Object Storage |
| **RNF10** - Performance | ⭐ | ✅ | ✅ | ⭐ | ⭐ | ✅ | ⭐ | ⭐ | ⭐ | Worker Runtime, API Gateway |

## 4. UC Coverage Analysis

### 4.1. Szczegółowe pokrycie wymagań przez UC

#### UC1 - Skonfiguruj i uruchom eksperyment benchmarkowy
**Pokrycie wymagań**: R1⭐, R2⭐, R4⭐, R5⭐, R6⭐, R15✅ + wszystkie RNF
- **Kluczowe dla**: Podstawowej funkcjonalności systemu
- **Komponenty**: Orchestrator, Web UI, Algorithm Registry, Benchmark Definition

#### UC2 - Przeglądaj katalog benchmarków  
**Pokrycie wymagań**: R1✅, R2✅, R4⭐, R15✅ + RNF1-2, RNF6, RNF8⭐
- **Kluczowe dla**: Eksploracji dostępnych benchmarków
- **Komponenty**: Benchmark Definition Service, Web UI

#### UC3 - Rejestracja własnego algorytmu HPO
**Pokrycie wymagań**: R2⭐, R3⭐, R13⭐, R15✅ + RNF3⭐, RNF5⭐, RNF8⭐  
- **Kluczowe dla**: Extensibility systemu
- **Komponenty**: Algorithm Registry, Plugin Runtime, Auth Service

#### UC4 - Porównaj wyniki algorytmów
**Pokrycie wymagań**: R8⭐, R11✅, R14✅ + RNF8⭐, RNF10⭐
- **Kluczowe dla**: Analizy wyników benchmarkingu
- **Komponenty**: MetricsAnalysisService, Web UI, Tracking

#### UC5 - Przeglądaj i filtruj eksperymenty  
**Pokrycie wymagań**: R7⭐, R9⭐ + RNF2⭐, RNF4⭐, RNF7⭐, RNF8⭐, RNF10⭐
- **Kluczowe dla**: Zarządzania historią eksperymentów  
- **Komponenty**: Experiment Tracking, Web UI

#### UC6 - Zarządzanie referencjami do publikacji
**Pokrycie wymagań**: R10⭐, R11✅ + RNF8⭐
- **Kluczowe dla**: Naukowego kontekstu algorytmów
- **Komponenty**: Publication Service, Web UI

#### UC7 - Deploy systemu lokalnie (PC)
**Pokrycie wymagań**: R6⭐, R15⭐ + RNF1⭐, RNF2⭐, RNF3⭐, RNF4⭐, RNF6⭐, RNF9⭐, RNF10⭐
- **Kluczowe dla**: PC-first deployment
- **Komponenty**: Wszystkie (docker-compose)

#### UC8 - Deploy systemu w chmurze (K8s)  
**Pokrycie wymagań**: R6⭐, R15⭐ + RNF1⭐, RNF2⭐, RNF3⭐, RNF4⭐, RNF6⭐, RNF9⭐, RNF10⭐
- **Kluczowe dla**: Cloud deployment i skalowania
- **Komponenty**: Wszystkie (Kubernetes)

#### UC9 - Integracja przez API
**Pokrycie wymagań**: R12⭐, R14⭐, R11⭐ + RNF3⭐, RNF5⭐, RNF8⭐, RNF10⭐
- **Kluczowe dla**: Programmatic access i integracji
- **Komponenty**: API Gateway, wszystkie serwisy

### 4.2. Gap Analysis - potencjalne braki

| Area | Gap Description | Risk Level | Mitigation |
|------|-----------------|------------|------------|
| **R8 Coverage** | Tylko UC4+UC5 pokrywają porównywanie | 🟡 Medium | UC4 jest comprehensive dla tego wymagania |
| **R13 Coverage** | SDK tylko w UC3+UC9 | 🟡 Medium | UC3 pokrywa komplexowo plugin development |
| **R11 Coverage** | Reporting w UC4+UC6+UC9 | 🟢 Low | Distributed reporting jest OK |
| **Performance Testing** | Brak dedykowanego UC dla load testing | 🟡 Medium | Dodać UC10 - Performance Testing |

## 5. Architecture Components vs Requirements

### 5.1. Macierz komponentów vs wymagań funkcjonalnych

| Komponent | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15 |
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

### 5.2. Komponenty vs wymagania niefunkcjonalne

| Komponent | RNF1 | RNF2 | RNF3 | RNF4 | RNF5 | RNF6 | RNF7 | RNF8 | RNF9 | RNF10 |
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

## 6. Rekomendacje

### 6.1. Priorytety implementacji

**Faza 1 - Core (UC1, UC2, UC7)**:
- Web UI, API Gateway, Orchestrator
- Algorithm Registry, Benchmark Definition  
- Basic deployment (docker-compose)

**Faza 2 - Extensions (UC3, UC5, UC6)**:
- Plugin Runtime, Algorithm SDK
- Experiment Tracking, Filtering
- Publication Service

**Faza 3 - Analytics (UC4, UC9)**:
- MetricsAnalysisService
- Advanced API, Export capabilities
- Reporting system

**Faza 4 - Scale (UC8)**:
- Kubernetes deployment
- Advanced monitoring, DR procedures
- Multi-tenant capabilities

### 6.2. Potential UC Extensions

- **UC10** - Performance benchmarking i load testing
- **UC11** - Multi-tenant organization management  
- **UC12** - Advanced alerting i notifications
- **UC13** - Batch experiment scheduling

## 7. Powiązane dokumenty

- **Wymagania funkcjonalne**: [Functional Requirements](functional-requirements.md)
- **Wymagania niefunkcjonalne**: [Non-functional Requirements](non-functional-requirements.md)
- **Przypadki użycia**: [Use Cases](use-cases.md)
- **Architektura systemu**: [C4 Model - Context](../architecture/c1-context.md)
- **Decyzje projektowe**: [Architecture Decision Records](../design/design-decisions.md)
- **Model danych**: [Data Model](../design/data-model.md)

## Cross-reference

- **Use Cases**: [Use Cases](use-cases.md)
- **Requirements**: [Functional Requirements](functional-requirements.md), [Non-functional Requirements](non-functional-requirements.md)
- **Architecture**: [C4 Components](../architecture/c3-components.md)
- **Data Model**: [Data Model](../design/data-model.md)
