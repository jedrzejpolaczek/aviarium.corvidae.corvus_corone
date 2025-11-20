# Wymagania funkcjonalne - Corvus Corone

> **Functional requirements dla systemu HPO Benchmarking Platform**

---

## 📚 R1 – Katalog algorytmów HPO (wbudowanych)

**Wymaganie:** System musi zawierać katalog wbudowanych algorytmów HPO gotowych do użycia.

**Kryteria akceptacji:**
- Podstawowe algorytmy: Random Search, Grid Search, Bayesian Optimization (TPE)
- Algorytmy ewolucyjne: Genetic Algorithm, Differential Evolution
- Gradient-based: CMA-ES, SMAC
- Metadane algorytmów: typ, parametry, kompatybilność z problemami
- Wersjonowanie algorytmów wbudowanych
- API do listowania i filtrowania algorytmów

---

## 🔌 R2 – Wsparcie dla algorytmów HPO jako pluginów

**Wymaganie:** System musi umożliwiać dodawanie własnych algorytmów HPO jako pluginów.

**Kryteria akceptacji:**
- Plugin SDK dla Python (minimum), docelowo R, Julia
- Standardowy interfejs IAlgorithmPlugin
- Container-based isolation pluginów
- Plugin registry z metadanymi
- Lifecycle management (install, activate, deactivate, uninstall)
- Security scanning pluginów przed rejestracją

---

## 🏷️ R3 – Wersjonowanie algorytmów HPO

**Wymaganie:** System musi obsługiwać wersjonowanie algorytmów (wbudowanych i pluginów).

**Kryteria akceptacji:**
- Semantic versioning (major.minor.patch)
- Backwards compatibility tracking
- Możliwość rollback do poprzedniej wersji
- Version pinning w eksperymentach
- Deprecation warnings dla starych wersji
- Migration paths między wersjami

---

## 📊 R4 – Katalog benchmarków

**Wymaganie:** System musi zawierać katalog benchmarków z definicjami problemów.

**Kryteria akceptacji:**
- Standard benchmarks: UCI datasets, synthetic problems
- Problem types: classification, regression, clustering
- Benchmark instances z metadanymi
- Best-known values gdzie dostępne
- Dataset versioning i checksums
- Custom benchmark definition support

---

## ⚙️ R5 – Konfiguracja eksperymentów benchmarkowych

**Wymaganie:** System musi umożliwiać łatwą konfigurację eksperymentów.

**Kryteria akceptacji:**
- Web UI do konfiguracji eksperymentów
- Dobór algorytmów i benchmarków
- Budget configuration (evaluations, time, resources)
- Seed management dla reprodukowalności
- Parameter space definition
- Validation przed uruchomieniem

---

## 🎯 R6 – Orkiestracja eksperymentów

**Wymaganie:** System musi zarządzać planowaniem i uruchamianiem eksperymentów.

**Kryteria akceptacji:**
- Queue management dla runów
- Priority scheduling (normal, high, low)
- Resource allocation i limits
- Retry policies dla failed runs
- Progress tracking w czasie rzeczywistym
- Graceful shutdown i resume

---

## 📱 R7 – Panel śledzenia eksperymentów

**Wymaganie:** System musi zapewniać dashboard do monitorowania eksperymentów.

**Kryteria akceptacji:**
- Lista eksperymentów z statusami
- Real-time metrics i progress bars
- Filtering i sorting eksperymentów
- Detailed view pojedynczych runów
- Log viewing i download
- Export experiment metadata

---

## 📈 R8 – Porównywanie wyników algorytmów

**Wymaganie:** System musi umożliwiać porównywanie wyników różnych algorytmów.

**Kryteria akceptacji:**
- Side-by-side comparison view
- Statistical significance tests
- Visualization: box plots, convergence curves, rankings
- Performance profiles i win/loss matrices
- Export comparison results
- Custom metrics definition

---

## 📋 R9 – Rejestrowanie i przegląd logów oraz artefaktów

**Wymaganie:** System musi zapisywać kompletne logi i artefakty z eksperymentów.

**Kryteria akceptacji:**
- Structured logging (JSON format)
- Artifact storage (models, plots, configs)
- Log search i filtering
- Artifact versioning
- Automatic cleanup policies
- Download i sharing capabilities

---

## 📚 R10 – Zarządzanie referencjami do publikacji

**Wymaganie:** System musi obsługiwać bibliografię i publikacje naukowe.

**Kryteria akceptacji:**
- Publication database z metadanymi
- DOI integration i automatic fetching
- BibTeX import/export
- Linking publications to algorithms/benchmarks
- Citation generation dla raportów
- CrossRef/arXiv integration

---

## 📄 R11 – Generowanie raportów

**Wymaganie:** System musi generować profesjonalne raporty z eksperymentów.

**Kryteria akceptacji:**
- HTML/PDF report generation
- Template-based reporting
- Bibliography i citations
- Experiment configuration documentation
- Statistical analysis inclusion
- Custom report templates

---

## 🔗 R12 – API do integracji ze światem zewnętrznym

**Wymaganie:** System musi zapewniać REST API dla integracji.

**Kryteria akceptacji:**
- RESTful API z OpenAPI specification
- Authentication i authorization
- Rate limiting i throttling
- Webhook support dla notifications
- Batch operations support
- API versioning i backwards compatibility

---

## 🛠️ R13 – API/SDK do tworzenia własnych algorytmów HPO

**Wymaganie:** System musi zapewniać SDK dla developerów algorytmów.

**Kryteria akceptacji:**
- Python SDK z clear interface
- Documentation i tutorials
- Example implementations
- Testing framework dla pluginów
- Packaging i distribution support
- Version compatibility matrix

---

## 📤 R14 – Eksport danych

**Wymaganie:** System musi umożliwiać eksport wyników do zewnętrznych formatów.

**Kryteria akceptacji:**
- Multiple formats: CSV, JSON, Parquet, HDF5
- Structured export z metadata
- Batch export capabilities
- Cloud storage integration (S3, GCS)
- Export job scheduling
- Data schema documentation

---

## 🖥️ R15 – Multi-environment deployment (PC-first, cloud-ready)

**Wymaganie:** System musi działać zarówno lokalnie (PC-first) jak i w chmurze (cloud-ready).

**Kryteria akceptacji:**
- Docker Compose dla local deployment
- Kubernetes manifests dla cloud
- Auto-scaling workkerów
- Environment-specific configuration
- Migration path PC → cloud
- Resource monitoring i optimization

---

## 🎯 Macierz wymagań vs komponenty

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

**Legenda:**
- ⭐ = Krytyczne wymaganie dla komponentu
- ✅ = Ważne wymaganie 
- - = Nie dotyczy

---

## Powiązane dokumenty

- **Requirements**: [Use Cases](use-cases.md), [Non-functional Requirements](non-functional-requirements.md)
- **Architektura**: [Kontekst (C4-1)](../architecture/c1-context.md), [Kontenery (C4-2)](../architecture/c2-containers.md)
- **Traceability**: [Requirements Traceability](requirements-traceability.md)
- **Design**: [Design Decisions](../design/design-decisions.md), [Data Model](../design/data-model.md)
