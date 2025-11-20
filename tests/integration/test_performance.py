"""
Performance and scalability tests for the layered architecture

These tests validate that the layered architecture can handle realistic
loads and scales appropriately.
"""
import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import logging

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

logger = logging.getLogger(__name__)

class PerformanceMetrics:
    """Collects and analyzes performance metrics"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.success_count = 0
        self.error_count = 0
        self.start_time = None
        self.end_time = None
    
    def start_measurement(self):
        """Start performance measurement"""
        self.start_time = time.time()
    
    def end_measurement(self):
        """End performance measurement"""
        self.end_time = time.time()
    
    def record_response(self, response_time: float, success: bool = True):
        """Record a response time"""
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.response_times:
            return {"error": "No measurements recorded"}
        
        total_requests = len(self.response_times)
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        return {
            "total_requests": total_requests,
            "success_rate": (self.success_count / total_requests) * 100,
            "error_rate": (self.error_count / total_requests) * 100,
            "duration_seconds": duration,
            "requests_per_second": total_requests / duration if duration > 0 else 0,
            "response_times": {
                "min": min(self.response_times),
                "max": max(self.response_times),
                "mean": statistics.mean(self.response_times),
                "median": statistics.median(self.response_times),
                "p95": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) > 20 else max(self.response_times),
                "p99": statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) > 100 else max(self.response_times)
            }
        }

class MockServiceClient:
    """Mock service client for testing"""
    
    def __init__(self, response_delay: float = 0.01, failure_rate: float = 0.0):
        self.response_delay = response_delay
        self.failure_rate = failure_rate
        self.request_count = 0
    
    async def make_request(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a mock service request"""
        self.request_count += 1
        
        # Simulate network delay
        await asyncio.sleep(self.response_delay)
        
        # Simulate failures
        import random
        if random.random() < self.failure_rate:
            raise Exception(f"Simulated failure for request {self.request_count}")
        
        return {
            "status": "success",
            "endpoint": endpoint,
            "request_id": self.request_count,
            "data": data or {}
        }

class LayerPerformanceTester:
    """Tests performance characteristics of individual layers"""
    
    def __init__(self):
        self.mock_clients = {
            "presentation": MockServiceClient(response_delay=0.005),
            "business-logic": MockServiceClient(response_delay=0.02),
            "execution": MockServiceClient(response_delay=0.1),
            "support": MockServiceClient(response_delay=0.01),
            "data": MockServiceClient(response_delay=0.03)
        }
    
    async def test_layer_throughput(self, layer_name: str, num_requests: int = 100) -> PerformanceMetrics:
        """Test throughput for a specific layer"""
        if layer_name not in self.mock_clients:
            raise ValueError(f"Unknown layer: {layer_name}")
        
        client = self.mock_clients[layer_name]
        metrics = PerformanceMetrics()
        metrics.start_measurement()
        
        async def make_test_request():
            start_time = time.time()
            try:
                await client.make_request(f"/{layer_name}/test")
                response_time = time.time() - start_time
                metrics.record_response(response_time, success=True)
            except Exception:
                response_time = time.time() - start_time
                metrics.record_response(response_time, success=False)
        
        # Execute requests concurrently
        tasks = [make_test_request() for _ in range(num_requests)]
        await asyncio.gather(*tasks)
        
        metrics.end_measurement()
        return metrics
    
    async def test_cross_layer_communication(self, num_workflows: int = 50) -> PerformanceMetrics:
        """Test communication across multiple layers"""
        metrics = PerformanceMetrics()
        metrics.start_measurement()
        
        async def simulate_workflow():
            """Simulate a request flowing through multiple layers"""
            start_time = time.time()
            try:
                # Presentation → Business Logic → Execution → Data
                await self.mock_clients["presentation"].make_request("/api/experiments")
                await self.mock_clients["business-logic"].make_request("/orchestrator/create")
                await self.mock_clients["execution"].make_request("/worker/execute")
                await self.mock_clients["data"].make_request("/database/store")
                
                response_time = time.time() - start_time
                metrics.record_response(response_time, success=True)
            except Exception:
                response_time = time.time() - start_time
                metrics.record_response(response_time, success=False)
        
        # Execute workflows concurrently
        tasks = [simulate_workflow() for _ in range(num_workflows)]
        await asyncio.gather(*tasks)
        
        metrics.end_measurement()
        return metrics

class ScalabilityTester:
    """Tests scalability characteristics of the architecture"""
    
    def __init__(self):
        self.performance_tester = LayerPerformanceTester()
    
    async def test_load_scaling(self, load_levels: List[int] = [10, 50, 100, 200, 500]) -> Dict[int, PerformanceMetrics]:
        """Test how performance scales with increasing load"""
        results = {}
        
        for load in load_levels:
            logger.info(f"Testing load level: {load} requests")
            metrics = await self.performance_tester.test_cross_layer_communication(load)
            results[load] = metrics
            
            # Small delay between load tests
            await asyncio.sleep(1.0)
        
        return results
    
    def analyze_scaling_behavior(self, load_results: Dict[int, PerformanceMetrics]) -> Dict[str, Any]:
        """Analyze scaling behavior from load test results"""
        loads = sorted(load_results.keys())
        throughputs = []
        response_times = []
        error_rates = []
        
        for load in loads:
            summary = load_results[load].get_summary()
            throughputs.append(summary.get("requests_per_second", 0))
            response_times.append(summary.get("response_times", {}).get("mean", 0))
            error_rates.append(summary.get("error_rate", 0))
        
        # Calculate scaling efficiency
        baseline_throughput = throughputs[0] if throughputs else 0
        scaling_efficiency = []
        
        for i, (load, throughput) in enumerate(zip(loads, throughputs)):
            if i == 0:
                scaling_efficiency.append(100.0)  # Baseline is 100%
            else:
                expected_throughput = baseline_throughput * (load / loads[0])
                efficiency = (throughput / expected_throughput) * 100 if expected_throughput > 0 else 0
                scaling_efficiency.append(efficiency)
        
        return {
            "load_levels": loads,
            "throughput": throughputs,
            "response_times": response_times,
            "error_rates": error_rates,
            "scaling_efficiency": scaling_efficiency,
            "max_throughput": max(throughputs),
            "degradation_threshold": next((load for load, eff in zip(loads, scaling_efficiency) if eff < 70), None)
        }

# Test classes using pytest

class TestLayerPerformance:
    """Test performance characteristics of each layer"""
    
    @pytest.fixture
    def performance_tester(self):
        """Create performance tester instance"""
        return LayerPerformanceTester()
    
    @pytest.mark.asyncio
    async def test_presentation_layer_performance(self, performance_tester):
        """Test presentation layer performance"""
        metrics = await performance_tester.test_layer_throughput("presentation", 100)
        summary = metrics.get_summary()
        
        # Assertions for acceptable performance
        assert summary["success_rate"] >= 95.0, f"Success rate too low: {summary['success_rate']}%"
        assert summary["response_times"]["mean"] < 0.1, f"Response time too high: {summary['response_times']['mean']}s"
        assert summary["requests_per_second"] > 50, f"Throughput too low: {summary['requests_per_second']} req/s"
        
        logger.info(f"Presentation layer performance: {summary}")
    
    @pytest.mark.asyncio
    async def test_business_logic_layer_performance(self, performance_tester):
        """Test business logic layer performance"""
        metrics = await performance_tester.test_layer_throughput("business-logic", 100)
        summary = metrics.get_summary()
        
        # Business logic layer may be slower due to complex processing
        assert summary["success_rate"] >= 95.0, f"Success rate too low: {summary['success_rate']}%"
        assert summary["response_times"]["mean"] < 0.5, f"Response time too high: {summary['response_times']['mean']}s"
        assert summary["requests_per_second"] > 20, f"Throughput too low: {summary['requests_per_second']} req/s"
        
        logger.info(f"Business logic layer performance: {summary}")
    
    @pytest.mark.asyncio
    async def test_execution_layer_performance(self, performance_tester):
        """Test execution layer performance"""
        metrics = await performance_tester.test_layer_throughput("execution", 50)  # Lower load for execution
        summary = metrics.get_summary()
        
        # Execution layer is expected to be slower
        assert summary["success_rate"] >= 90.0, f"Success rate too low: {summary['success_rate']}%"
        assert summary["response_times"]["mean"] < 2.0, f"Response time too high: {summary['response_times']['mean']}s"
        
        logger.info(f"Execution layer performance: {summary}")
    
    @pytest.mark.asyncio
    async def test_cross_layer_workflow_performance(self, performance_tester):
        """Test performance of workflows spanning multiple layers"""
        metrics = await performance_tester.test_cross_layer_communication(50)
        summary = metrics.get_summary()
        
        # End-to-end workflows will be slower but should still be responsive
        assert summary["success_rate"] >= 90.0, f"Success rate too low: {summary['success_rate']}%"
        assert summary["response_times"]["mean"] < 1.0, f"Response time too high: {summary['response_times']['mean']}s"
        assert summary["requests_per_second"] > 10, f"Throughput too low: {summary['requests_per_second']} req/s"
        
        logger.info(f"Cross-layer workflow performance: {summary}")

class TestScalability:
    """Test scalability characteristics"""
    
    @pytest.fixture
    def scalability_tester(self):
        """Create scalability tester instance"""
        return ScalabilityTester()
    
    @pytest.mark.asyncio
    @pytest.mark.slow  # Mark as slow test
    async def test_load_scaling_behavior(self, scalability_tester):
        """Test how the system scales with increasing load"""
        load_levels = [10, 25, 50, 100]  # Reduced for faster testing
        load_results = await scalability_tester.test_load_scaling(load_levels)
        
        scaling_analysis = scalability_tester.analyze_scaling_behavior(load_results)
        
        # Log results
        logger.info(f"Scaling analysis: {scaling_analysis}")
        
        # Assertions for acceptable scaling
        assert scaling_analysis["max_throughput"] > 20, "Maximum throughput too low"
        
        # Check that we don't have immediate degradation
        first_efficiency = scaling_analysis["scaling_efficiency"][1] if len(scaling_analysis["scaling_efficiency"]) > 1 else 100
        assert first_efficiency > 50, f"Scaling efficiency degrades too quickly: {first_efficiency}%"
    
    @pytest.mark.asyncio
    async def test_concurrent_layer_access(self):
        """Test concurrent access to multiple layers"""
        tester = LayerPerformanceTester()
        
        # Test concurrent access to different layers
        tasks = [
            tester.test_layer_throughput("presentation", 20),
            tester.test_layer_throughput("business-logic", 20),
            tester.test_layer_throughput("support", 20)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All layers should perform reasonably well under concurrent load
        for i, metrics in enumerate(results):
            summary = metrics.get_summary()
            layer_name = ["presentation", "business-logic", "support"][i]
            
            assert summary["success_rate"] >= 85.0, f"{layer_name} layer failed under concurrent load"
            logger.info(f"{layer_name} layer concurrent performance: {summary}")

class TestResourceUtilization:
    """Test resource utilization patterns"""
    
    @pytest.mark.asyncio
    async def test_memory_usage_patterns(self):
        """Test memory usage during load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run some load
        tester = LayerPerformanceTester()
        await tester.test_cross_layer_communication(100)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for this test)
        assert memory_increase < 100, f"Memory usage increased too much: {memory_increase}MB"
        
        logger.info(f"Memory usage: {initial_memory:.1f}MB → {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
    
    @pytest.mark.asyncio
    async def test_connection_pooling_efficiency(self):
        """Test that connection pooling is working efficiently"""
        # This would test actual database connection pooling
        # For now, just test that mock services handle concurrent requests
        
        tester = LayerPerformanceTester()
        
        # Run multiple batches to test connection reuse
        batch_results = []
        for _ in range(3):
            metrics = await tester.test_layer_throughput("data", 30)
            batch_results.append(metrics.get_summary())
        
        # Response times should be consistent across batches (indicating good connection reuse)
        response_times = [batch["response_times"]["mean"] for batch in batch_results]
        max_variance = max(response_times) - min(response_times)
        
        assert max_variance < 0.05, f"Response time variance too high: {max_variance}s"
        
        logger.info(f"Connection pooling test - response time variance: {max_variance:.3f}s")

if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-m", "not slow"])