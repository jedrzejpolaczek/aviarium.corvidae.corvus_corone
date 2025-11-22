import json
import logging
import os
import time
import traceback
from datetime import datetime
from typing import Dict, Any, List

import httpx
import numpy as np
import pika
from minio import Minio
from minio.error import S3Error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:admin@rabbitmq:5672")
TRACKING_SERVICE_URL = os.getenv("TRACKING_SERVICE_URL", "http://experiment-tracking:8002")
BENCHMARK_SERVICE_URL = os.getenv("BENCHMARK_SERVICE_URL", "http://benchmark-definition:8003")
ALGORITHM_REGISTRY_URL = os.getenv("ALGORITHM_REGISTRY_URL", "http://algorithm-registry:8004")
OBJECT_STORAGE_URL = os.getenv("OBJECT_STORAGE_URL", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
WORKER_ID = os.getenv("WORKER_ID", f"worker-{int(time.time())}")

class HPOWorker:
    """HPO Algorithm execution worker"""
    
    def __init__(self):
        self.worker_id = WORKER_ID
        self.connection = None
        self.channel = None
        self.minio_client = None
        self._setup_connections()
    
    def _setup_connections(self):
        """Setup RabbitMQ and MinIO connections"""
        try:
            # RabbitMQ connection
            self.connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='hpo_runs', durable=True)
            self.channel.basic_qos(prefetch_count=1)
            
            # MinIO connection
            minio_url = OBJECT_STORAGE_URL.replace("http://", "").replace("https://", "")
            self.minio_client = Minio(
                minio_url,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=False
            )
            
            # Ensure bucket exists
            if not self.minio_client.bucket_exists("hpo-artifacts"):
                self.minio_client.make_bucket("hpo-artifacts")
            
            logger.info(f"Worker {self.worker_id} connections established")
            
        except Exception as e:
            logger.error(f"Failed to setup connections: {e}")
            raise
    
    def start_consuming(self):
        """Start consuming run jobs from queue"""
        logger.info(f"Worker {self.worker_id} starting to consume jobs")
        
        self.channel.basic_consume(
            queue='hpo_runs',
            on_message_callback=self._process_run_job,
            auto_ack=False
        )
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
            self.channel.stop_consuming()
            self.connection.close()
    
    def _process_run_job(self, ch, method, properties, body):
        """Process a single run job"""
        try:
            # Parse job message
            job = json.loads(body.decode())
            run_id = job["run_id"]
            
            logger.info(f"Processing run {run_id}")
            
            # Update run status to running
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            loop.run_until_complete(self._update_run_status(run_id, "running", start_time=datetime.utcnow()))
            
            # Execute the run
            result = loop.run_until_complete(self._execute_run(job))
            
            if result["success"]:
                # Update run status to completed
                loop.run_until_complete(self._update_run_status(
                    run_id, 
                    "completed", 
                    end_time=datetime.utcnow(),
                    resource_usage=result["resource_usage"]
                ))
                logger.info(f"Run {run_id} completed successfully")
            else:
                # Update run status to failed
                loop.run_until_complete(self._update_run_status(
                    run_id, 
                    "failed", 
                    end_time=datetime.utcnow(),
                    error_message=result["error"]
                ))
                logger.error(f"Run {run_id} failed: {result['error']}")
            
            loop.close()
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing job: {e}")
            logger.error(traceback.format_exc())
            
            # Try to update run status to failed
            try:
                if 'run_id' in locals() and 'loop' in locals():
                    loop.run_until_complete(self._update_run_status(
                        run_id, 
                        "failed", 
                        end_time=datetime.utcnow(),
                        error_message=str(e)
                    ))
            except:
                logger.error("Failed to update run status after error")
            
            # Reject message (don't requeue to avoid infinite loops)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    async def _execute_run(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HPO algorithm run"""
        run_id = job["run_id"]
        algorithm_config = job["algorithm_config"]
        benchmark_id = job["benchmark_id"]
        instance_id = job["instance_id"]
        seed = job["seed"]
        
        start_time = time.time()
        
        try:
            # 1. Load benchmark data
            benchmark_data = await self._load_benchmark_data(benchmark_id, instance_id)
            
            # 2. Load algorithm
            algorithm_info = await self._load_algorithm_info(algorithm_config["algorithm_id"])
            
            # 3. Execute HPO algorithm
            if algorithm_info["is_builtin"]:
                result = await self._execute_builtin_algorithm(
                    algorithm_config, benchmark_data, seed, run_id
                )
            else:
                result = await self._execute_plugin_algorithm(
                    algorithm_config, benchmark_data, seed, run_id
                )
            
            execution_time = time.time() - start_time
            
            # 4. Store artifacts and log metrics
            if result["success"]:
                await self._store_run_artifacts(run_id, result["artifacts"])
                await self._log_run_metrics(run_id, result["metrics"])
            
            return {
                "success": result["success"],
                "error": result.get("error"),
                "resource_usage": {
                    "execution_time_seconds": execution_time,
                    "worker_id": self.worker_id
                }
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Run execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "resource_usage": {
                    "execution_time_seconds": execution_time,
                    "worker_id": self.worker_id
                }
            }
    
    async def _load_benchmark_data(self, benchmark_id: str, instance_id: str) -> Dict[str, Any]:
        """Load benchmark data from benchmark service"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BENCHMARK_SERVICE_URL}/api/benchmarks/{benchmark_id}/instances/{instance_id}/data"
            )
            if response.status_code != 200:
                raise Exception(f"Failed to load benchmark data: {response.text}")
            return response.json()
    
    async def _load_algorithm_info(self, algorithm_id: str) -> Dict[str, Any]:
        """Load algorithm information from algorithm registry"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ALGORITHM_REGISTRY_URL}/api/algorithms/{algorithm_id}"
            )
            if response.status_code != 200:
                raise Exception(f"Failed to load algorithm info: {response.text}")
            return response.json()
    
    async def _execute_builtin_algorithm(
        self, 
        algorithm_config: Dict[str, Any], 
        benchmark_data: Dict[str, Any], 
        seed: int,
        run_id: str
    ) -> Dict[str, Any]:
        """Execute built-in HPO algorithm"""
        algorithm_id = algorithm_config["algorithm_id"]
        parameters = algorithm_config.get("parameters", {})
        budget_limit = algorithm_config.get("budget_limit", 100)
        
        logger.info(f"Executing built-in algorithm {algorithm_id} for run {run_id}")
        
        # Set random seed
        np.random.seed(seed)
        
        try:
            if algorithm_id == "random_search":
                result = await self._run_random_search(
                    benchmark_data, budget_limit, parameters, run_id
                )
            elif algorithm_id == "bayesian_optimization":
                result = await self._run_bayesian_optimization(
                    benchmark_data, budget_limit, parameters, run_id
                )
            elif algorithm_id == "grid_search":
                result = await self._run_grid_search(
                    benchmark_data, budget_limit, parameters, run_id
                )
            else:
                raise Exception(f"Unknown built-in algorithm: {algorithm_id}")
            
            return {
                "success": True,
                "metrics": result["metrics"],
                "artifacts": result["artifacts"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _run_random_search(
        self, 
        benchmark_data: Dict[str, Any], 
        budget_limit: int, 
        parameters: Dict[str, Any],
        run_id: str
    ) -> Dict[str, Any]:
        """Run Random Search algorithm"""
        metrics = []
        artifacts = []
        
        # Extract benchmark configuration
        param_space = benchmark_data["parameter_space"]
        objective_function = benchmark_data["objective_function"]
        
        best_value = float('inf')
        best_params = None
        evaluation_history = []
        
        # Random search iterations
        for iteration in range(budget_limit):
            # Sample random parameters
            params = {}
            for param_name, param_config in param_space.items():
                if param_config["type"] == "float":
                    params[param_name] = np.random.uniform(
                        param_config["min"], param_config["max"]
                    )
                elif param_config["type"] == "int":
                    params[param_name] = np.random.randint(
                        param_config["min"], param_config["max"] + 1
                    )
                elif param_config["type"] == "categorical":
                    params[param_name] = np.random.choice(param_config["choices"])
            
            # Evaluate objective function (simulated)
            objective_value = self._simulate_objective_function(
                params, objective_function, iteration
            )
            
            evaluation_history.append({
                "iteration": iteration,
                "parameters": params,
                "objective_value": objective_value
            })
            
            # Update best
            if objective_value < best_value:
                best_value = objective_value
                best_params = params
            
            # Log metric for this iteration
            metrics.append({
                "name": "objective",
                "value": objective_value,
                "step": iteration
            })
            
            metrics.append({
                "name": "best_so_far",
                "value": best_value,
                "step": iteration
            })
            
            # Log progress every 10 iterations
            if iteration % 10 == 0:
                logger.info(f"Random search iteration {iteration}, best: {best_value:.6f}")
        
        # Create convergence plot data
        convergence_data = {
            "iterations": [h["iteration"] for h in evaluation_history],
            "objective_values": [h["objective_value"] for h in evaluation_history],
            "best_values": [min([h["objective_value"] for h in evaluation_history[:i+1]]) 
                           for i in range(len(evaluation_history))]
        }
        
        artifacts.append({
            "name": "convergence_data.json",
            "type": "convergence_plot",
            "data": convergence_data
        })
        
        artifacts.append({
            "name": "evaluation_history.json",
            "type": "evaluation_log",
            "data": evaluation_history
        })
        
        # Final metrics
        metrics.append({
            "name": "final_best_value",
            "value": best_value,
            "step": budget_limit - 1
        })
        
        metrics.append({
            "name": "total_evaluations",
            "value": budget_limit,
            "step": budget_limit - 1
        })
        
        return {
            "metrics": metrics,
            "artifacts": artifacts
        }
    
    async def _run_bayesian_optimization(
        self, 
        benchmark_data: Dict[str, Any], 
        budget_limit: int, 
        parameters: Dict[str, Any],
        run_id: str
    ) -> Dict[str, Any]:
        """Run Bayesian Optimization (simplified TPE-like approach)"""
        # For simplicity, this is a basic implementation
        # In production, you'd use libraries like Optuna, Hyperopt, or scikit-optimize
        
        # Use random search as a placeholder for now
        # TODO: Implement proper Bayesian optimization
        return await self._run_random_search(benchmark_data, budget_limit, parameters, run_id)
    
    async def _run_grid_search(
        self, 
        benchmark_data: Dict[str, Any], 
        budget_limit: int, 
        parameters: Dict[str, Any],
        run_id: str
    ) -> Dict[str, Any]:
        """Run Grid Search algorithm"""
        # For simplicity, implement a basic grid search
        # In production, you'd implement proper grid generation
        
        # Use random search as a placeholder for now
        # TODO: Implement proper grid search
        return await self._run_random_search(benchmark_data, budget_limit, parameters, run_id)
    
    def _simulate_objective_function(
        self, 
        params: Dict[str, Any], 
        objective_config: Dict[str, Any], 
        iteration: int
    ) -> float:
        """Simulate objective function evaluation"""
        # This is a simulation - in real scenarios, this would train ML models
        
        # Add some noise and structure to make it realistic
        base_value = sum(hash(str(v)) % 1000 for v in params.values()) / 1000.0
        noise = np.random.normal(0, 0.1)
        
        # Simulate convergence by adding slight improvement over time
        improvement = -0.001 * iteration
        
        return base_value + noise + improvement
    
    async def _execute_plugin_algorithm(
        self, 
        algorithm_config: Dict[str, Any], 
        benchmark_data: Dict[str, Any], 
        seed: int,
        run_id: str
    ) -> Dict[str, Any]:
        """Execute plugin HPO algorithm"""
        # TODO: Implement plugin system
        # For now, return error
        return {
            "success": False,
            "error": "Plugin algorithms not yet implemented"
        }
    
    async def _store_run_artifacts(self, run_id: str, artifacts: List[Dict[str, Any]]):
        """Store run artifacts in object storage"""
        for artifact in artifacts:
            try:
                artifact_name = artifact["name"]
                artifact_data = json.dumps(artifact["data"]).encode()
                storage_path = f"runs/{run_id}/{artifact_name}"
                
                # Upload to MinIO
                self.minio_client.put_object(
                    "hpo-artifacts",
                    storage_path,
                    data=artifact_data,
                    length=len(artifact_data),
                    content_type="application/json"
                )
                
                # Register with tracking service
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{TRACKING_SERVICE_URL}/api/tracking/artifacts",
                        json={
                            "run_id": run_id,
                            "name": artifact_name,
                            "artifact_type": artifact["type"],
                            "storage_path": storage_path,
                            "size_bytes": len(artifact_data),
                            "content_type": "application/json"
                        }
                    )
                
                logger.info(f"Stored artifact {artifact_name} for run {run_id}")
                
            except Exception as e:
                logger.error(f"Failed to store artifact {artifact['name']}: {e}")
    
    async def _log_run_metrics(self, run_id: str, metrics: List[Dict[str, Any]]):
        """Log run metrics to tracking service"""
        try:
            # Prepare metrics for batch logging
            metric_requests = []
            for metric in metrics:
                metric_requests.append({
                    "run_id": run_id,
                    "name": metric["name"],
                    "value": metric["value"],
                    "step": metric["step"],
                    "metadata": {}
                })
            
            # Log metrics in batch
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{TRACKING_SERVICE_URL}/api/tracking/metrics/batch",
                    json=metric_requests
                )
                
                if response.status_code == 200:
                    logger.info(f"Logged {len(metrics)} metrics for run {run_id}")
                else:
                    logger.error(f"Failed to log metrics: {response.text}")
                    
        except Exception as e:
            logger.error(f"Failed to log metrics for run {run_id}: {e}")
    
    async def _update_run_status(
        self, 
        run_id: str, 
        status: str, 
        start_time: datetime = None,
        end_time: datetime = None,
        resource_usage: Dict[str, Any] = None,
        error_message: str = None
    ):
        """Update run status in tracking service"""
        try:
            update_data = {"status": status}
            
            if start_time:
                update_data["start_time"] = start_time.isoformat()
            if end_time:
                update_data["end_time"] = end_time.isoformat()
            if resource_usage:
                update_data["resource_usage"] = resource_usage
            if error_message:
                update_data["error_message"] = error_message
            
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{TRACKING_SERVICE_URL}/api/tracking/runs/{run_id}",
                    json=update_data
                )
                
                if response.status_code == 200:
                    logger.info(f"Updated run {run_id} status to {status}")
                else:
                    logger.error(f"Failed to update run status: {response.text}")
                    
        except Exception as e:
            logger.error(f"Failed to update run status: {e}")

def main():
    """Main worker entry point"""
    logger.info(f"Starting HPO Worker {WORKER_ID}")
    
    worker = HPOWorker()
    
    try:
        worker.start_consuming()
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        raise

if __name__ == "__main__":
    main()