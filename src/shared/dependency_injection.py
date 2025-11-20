"""
Dependency Injection Container for Corvus Corone Platform

This module provides a simple dependency injection system to manage
dependencies between layers and services while maintaining loose coupling.
"""
import logging
from typing import Dict, Any, TypeVar, Type, Optional, Callable
from abc import ABC, abstractmethod
import asyncio

logger = logging.getLogger(__name__)

T = TypeVar('T')

class DIContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._initialized = False
    
    def register_singleton(self, service_name: str, instance: Any):
        """Register a singleton instance"""
        self._singletons[service_name] = instance
        logger.debug(f"Registered singleton: {service_name}")
    
    def register_factory(self, service_name: str, factory: Callable):
        """Register a factory function for a service"""
        self._factories[service_name] = factory
        logger.debug(f"Registered factory: {service_name}")
    
    def register_service(self, service_name: str, service_instance: Any):
        """Register a service instance"""
        self._services[service_name] = service_instance
        logger.debug(f"Registered service: {service_name}")
    
    def get(self, service_name: str) -> Any:
        """Get a service instance"""
        # Check singletons first
        if service_name in self._singletons:
            return self._singletons[service_name]
        
        # Check registered services
        if service_name in self._services:
            return self._services[service_name]
        
        # Check factories
        if service_name in self._factories:
            instance = self._factories[service_name]()
            # Cache as singleton if it's a factory
            self._singletons[service_name] = instance
            return instance
        
        raise ValueError(f"Service '{service_name}' not found in container")
    
    def has(self, service_name: str) -> bool:
        """Check if a service is registered"""
        return (service_name in self._singletons or 
                service_name in self._services or 
                service_name in self._factories)
    
    async def initialize_async_services(self):
        """Initialize services that require async setup"""
        if self._initialized:
            return
        
        # Initialize any async services here
        for service_name, instance in self._services.items():
            if hasattr(instance, 'initialize_async'):
                try:
                    await instance.initialize_async()
                    logger.info(f"Initialized async service: {service_name}")
                except Exception as e:
                    logger.error(f"Failed to initialize {service_name}: {e}")
        
        self._initialized = True
    
    async def cleanup(self):
        """Cleanup services on shutdown"""
        for service_name, instance in self._services.items():
            if hasattr(instance, 'cleanup'):
                try:
                    await instance.cleanup()
                    logger.info(f"Cleaned up service: {service_name}")
                except Exception as e:
                    logger.error(f"Failed to cleanup {service_name}: {e}")

# Global container instance
container = DIContainer()

class ServiceRegistry:
    """Registry for layer-specific service dependencies"""
    
    def __init__(self, container: DIContainer):
        self.container = container
        self.layer_dependencies = {
            "presentation": ["support", "business-logic"],
            "business-logic": ["execution", "support", "data"],
            "execution": ["support", "data"],
            "support": ["data"],
            "data": []
        }
    
    def register_layer_services(self, layer_name: str, services: Dict[str, Any]):
        """Register all services for a specific layer"""
        for service_name, service_instance in services.items():
            full_service_name = f"{layer_name}.{service_name}"
            self.container.register_service(full_service_name, service_instance)
        
        logger.info(f"Registered {len(services)} services for {layer_name} layer")
    
    def get_layer_service(self, layer_name: str, service_name: str) -> Any:
        """Get a service from a specific layer"""
        full_service_name = f"{layer_name}.{service_name}"
        return self.container.get(full_service_name)
    
    def validate_dependencies(self, layer_name: str) -> bool:
        """Validate that a layer's dependencies are satisfied"""
        if layer_name not in self.layer_dependencies:
            logger.warning(f"Unknown layer: {layer_name}")
            return False
        
        required_layers = self.layer_dependencies[layer_name]
        for required_layer in required_layers:
            # Check if required layer has at least one registered service
            layer_services = [name for name in self.container._services.keys() 
                            if name.startswith(f"{required_layer}.")]
            if not layer_services:
                logger.error(f"Layer {layer_name} requires {required_layer} but no services found")
                return False
        
        return True

# Global registry instance
service_registry = ServiceRegistry(container)

def inject_dependencies(**dependencies):
    """Decorator for dependency injection"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Inject dependencies from container
            for dep_name, service_name in dependencies.items():
                if dep_name not in kwargs:
                    try:
                        kwargs[dep_name] = container.get(service_name)
                    except ValueError as e:
                        logger.error(f"Failed to inject dependency {dep_name}: {e}")
                        raise
            
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

class LayerInterface(ABC):
    """Abstract base class for layer interfaces"""
    
    @abstractmethod
    async def initialize(self):
        """Initialize the layer"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the layer"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup resources"""
        pass

def setup_dependency_injection():
    """Setup the dependency injection container with default services"""
    
    # This would be called during application startup
    # to register all the services and their dependencies
    
    logger.info("Setting up dependency injection container")
    
    # Example service registrations would go here
    # In practice, each layer would register its own services
    
    return container

async def initialize_all_layers():
    """Initialize all layers in dependency order"""
    layer_order = ["data", "support", "execution", "business-logic", "presentation"]
    
    for layer in layer_order:
        try:
            # Validate dependencies
            if not service_registry.validate_dependencies(layer):
                logger.error(f"Failed to validate dependencies for {layer} layer")
                continue
            
            logger.info(f"Initializing {layer} layer")
            # Additional layer initialization logic would go here
            
        except Exception as e:
            logger.error(f"Failed to initialize {layer} layer: {e}")
            raise
    
    # Initialize async services
    await container.initialize_async_services()
    
    logger.info("All layers initialized successfully")

# Utility functions for common dependency patterns

def get_service_client(service_name: str):
    """Get HTTP client for inter-service communication"""
    return container.get(f"clients.{service_name}")

def get_database_connection(db_name: str = "default"):
    """Get database connection"""
    return container.get(f"database.{db_name}")

def get_message_broker():
    """Get message broker connection"""
    return container.get("messaging.broker")

def get_config(service_name: str):
    """Get configuration for a service"""
    return container.get(f"config.{service_name}")

# Health check aggregator
async def check_all_layers_health() -> Dict[str, Any]:
    """Check health of all layers"""
    health_results = {}
    
    for layer in ["presentation", "business-logic", "execution", "support", "data"]:
        try:
            # This would check health of all services in the layer
            health_results[layer] = {"status": "healthy", "services": []}
        except Exception as e:
            health_results[layer] = {"status": "unhealthy", "error": str(e)}
    
    return health_results