# Architecture Decision Record: Layered Architecture Implementation

## Status
Accepted

## Context
The Corvus Corone HPO Benchmarking Platform was initially implemented with a flat microservices structure. To improve maintainability, scalability, and align with the documented C4 architecture model, we need to reorganize the codebase into a proper layered architecture.

## Decision
We will implement a layered architecture following the C4 model pattern:

```
Layers → Containers → Components
```

### Layer Structure:
1. **Presentation Layer**: User interfaces and external API access points
2. **Business Logic Layer**: Core domain services and business rules
3. **Execution Layer**: Runtime and execution environments
4. **Support Layer**: Cross-cutting concerns (auth, monitoring, etc.)
5. **Data Layer**: Data persistence and storage abstractions

### Component Organization:
Each service (container) follows this pattern:
```
service-name/
├── components/          # Service-specific business logic components
├── shared/             # Utilities and common code for the service
├── main.py            # FastAPI application entry point
├── Dockerfile         # Container configuration
└── requirements.txt   # Python dependencies
```

## Consequences

### Positive:
- **Clear Separation of Concerns**: Each layer has distinct responsibilities
- **Improved Maintainability**: Related functionality is logically grouped
- **Better Scalability**: Services can be scaled based on layer demands
- **Enhanced Testability**: Components can be tested in isolation
- **Documentation Alignment**: Structure matches C4 architecture documentation
- **Dependency Management**: Clear dependency flow from upper to lower layers

### Negative:
- **Initial Complexity**: More files and directories to manage
- **Migration Effort**: Existing code needs to be refactored
- **Learning Curve**: Developers need to understand the layer boundaries

## Implementation Guidelines

### Layer Dependencies:
- Upper layers can depend on lower layers, never the reverse
- Cross-layer communication should be explicit and well-defined
- Use dependency injection for layer interactions

### Component Guidelines:
- Business logic goes in `components/` directories
- Shared utilities and configuration go in `shared/` directories
- Each component should have a single responsibility
- Components should be loosely coupled and highly cohesive

### Service Communication:
- Use message queues (RabbitMQ) for asynchronous communication
- HTTP APIs for synchronous communication between layers
- Event-driven architecture for decoupling services

## Alternative Considered
We considered keeping the flat microservices structure, but this would have:
- Made the codebase harder to maintain as it grows
- Created inconsistency with the documented architecture
- Made it difficult to enforce proper separation of concerns

## Notes
This ADR should be reviewed and updated as the layered architecture evolves and we gain experience with the implementation.