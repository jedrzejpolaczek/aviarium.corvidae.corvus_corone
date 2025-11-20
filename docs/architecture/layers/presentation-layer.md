# Presentation Layer Documentation

The **Presentation Layer** is responsible for all user-facing interfaces and external API access points in the Corvus Corone HPO Benchmarking Platform.

## Layer Responsibilities

### Primary Functions:
- **User Interface Management**: Web-based interfaces for experiment design and monitoring
- **API Gateway**: Central entry point for all external API requests
- **Request Routing**: Intelligent routing of requests to appropriate backend services
- **Authentication Enforcement**: Token validation and user session management
- **Response Formatting**: Consistent API response structure and error handling

### Services in this Layer:

## 🌐 Web UI (`web-ui`)
**Purpose**: Bootstrap-based web frontend for experiment management

### Components:
- **ExperimentDesignerUI**: Interface for creating and configuring experiments
- **TrackingDashboardUI**: Real-time experiment monitoring and progress tracking
- **ComparisonViewUI**: Side-by-side comparison of algorithm performance
- **BenchmarkCatalogUI**: Browse and select benchmark problems
- **AlgorithmCatalogUI**: Explore available HPO algorithms 
- **PublicationManagerUI**: Manage research publications and citations
- **AdminSettingsUI**: System administration and configuration

### Shared Utilities:
- **UI Components**: Reusable UI elements and widgets
- **Configuration Management**: Frontend configuration and theming
- **API Client**: JavaScript client for backend communication

### Technologies:
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Build**: Nginx for static file serving
- **Responsive**: Mobile-friendly responsive design

## 🚪 API Gateway (`api-gateway`)
**Purpose**: Central API gateway and request router

### Components:
- **AuthenticationComponent**: JWT token validation and user authentication
- **ServiceRouter**: Intelligent request routing to backend services
- **PublicAPI**: External API endpoints and documentation

### Shared Utilities:
- **GatewayConfig**: Configuration management and environment settings
- **Middleware**: CORS, security headers, rate limiting
- **Response Models**: Standardized API response formats
- **Error Handling**: Consistent error responses and logging

### Key Features:
- **Service Discovery**: Automatic routing to healthy backend services
- **Load Balancing**: Distribute requests across service instances
- **Rate Limiting**: Protect backend services from overload
- **Request/Response Transformation**: Format adaptation between external and internal APIs
- **Health Monitoring**: Continuous health checks of backend services

### Technologies:
- **Framework**: FastAPI with async/await support
- **Authentication**: JWT token validation
- **Proxy**: HTTP client for service communication
- **Monitoring**: Prometheus metrics collection

## Architecture Patterns

### Request Flow:
1. **Client Request** → Web UI or Direct API
2. **API Gateway** → Authentication & Routing
3. **Backend Services** → Business logic processing
4. **Response** → Formatted and returned to client

### Security Model:
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Role-Based Access**: User roles control access to different features
- **CORS Policy**: Configurable cross-origin request handling
- **Security Headers**: Standard security headers for web protection

### Error Handling:
- **Consistent Format**: All errors follow standard structure
- **Error Codes**: HTTP status codes with detailed error messages
- **Logging**: Comprehensive error logging for debugging
- **User-Friendly**: Clear error messages for end users

## Configuration

### Environment Variables:
```bash
# Service URLs
AUTH_SERVICE_URL=http://auth-service:8001
ORCHESTRATOR_SERVICE_URL=http://experiment-orchestrator:8000
TRACKING_SERVICE_URL=http://experiment-tracking:8002

# CORS Configuration  
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_CREDENTIALS=true

# Security
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Monitoring
LOG_LEVEL=INFO
METRICS_ENABLED=true
```

## Dependencies

### Layer Dependencies:
- **Business Logic Layer**: For core experiment and algorithm management
- **Support Layer**: For authentication and monitoring services
- **External Systems**: For user authentication providers (optional)

### Technology Dependencies:
- **FastAPI**: Web framework for API gateway
- **Bootstrap 5**: UI framework for web interface
- **httpx**: HTTP client for service communication
- **Prometheus**: Metrics collection and monitoring

## Development Guidelines

### Component Development:
1. **Single Responsibility**: Each component handles one specific concern
2. **Dependency Injection**: Use constructor injection for dependencies
3. **Error Handling**: Implement comprehensive error handling
4. **Logging**: Add appropriate logging for debugging and monitoring
5. **Testing**: Unit tests for components, integration tests for workflows

### UI Development:
1. **Responsive Design**: Ensure mobile compatibility
2. **Accessibility**: Follow WCAG guidelines for accessibility
3. **Performance**: Optimize for fast loading and smooth interactions
4. **User Experience**: Intuitive navigation and clear feedback

### API Design:
1. **RESTful**: Follow REST principles for API design
2. **Versioning**: Include version information in API paths
3. **Documentation**: Automatic API documentation with OpenAPI/Swagger
4. **Consistency**: Consistent request/response formats across endpoints

## Deployment Considerations

### Scaling:
- **API Gateway**: Scale horizontally based on traffic
- **Web UI**: Static file serving can use CDN for global distribution
- **Load Balancing**: Use load balancer for multiple gateway instances

### Monitoring:
- **Health Checks**: Regular health checks for all components
- **Performance Metrics**: Response times, error rates, throughput
- **User Analytics**: Track user interactions and feature usage
- **Alerting**: Automated alerts for system issues

### Security:
- **HTTPS Only**: Enforce HTTPS for all external communication
- **Token Rotation**: Regular JWT token rotation
- **Input Validation**: Comprehensive input validation and sanitization
- **Audit Logging**: Log all user actions for security auditing