"""
Run scheduling and job queue management components
"""
import logging
from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime
from .planning import RunConfig, RunStatus, experiment_plan_builder

logger = logging.getLogger(__name__)

class RunScheduler:
    """Manages scheduling and queuing of experiment runs"""
    
    def __init__(self):
        self.message_broker = None  # Will be initialized with actual broker
        self.active_runs: Dict[str, RunConfig] = {}
        self.run_queue: List[str] = []  # Queue of run IDs
        self.max_concurrent_runs = 10
    
    async def initialize_broker(self, rabbitmq_url: str):
        """Initialize message broker connection"""
        try:
            import pika
            import json
            
            connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
            channel = connection.channel()
            
            # Declare queues
            channel.queue_declare(queue='experiment_runs', durable=True)
            channel.queue_declare(queue='run_results', durable=True)
            
            self.message_broker = {
                'connection': connection,
                'channel': channel
            }
            
            logger.info("Message broker initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize message broker: {e}")
            # Fall back to in-memory queue for development
            self.message_broker = None
    
    async def schedule_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Schedule all runs for an experiment"""
        try:
            # Get execution plan
            plan = await experiment_plan_builder.get_plan(experiment_id)
            if not plan:
                raise ValueError(f"No execution plan found for experiment {experiment_id}")
            
            # Add pending runs to queue
            pending_runs = [run for run in plan.runs if run.status == RunStatus.PENDING]
            
            scheduled_count = 0
            for run in pending_runs:
                await self._queue_run(run)
                scheduled_count += 1
            
            logger.info(f"Scheduled {scheduled_count} runs for experiment {experiment_id}")
            
            return {
                "experiment_id": experiment_id,
                "scheduled_runs": scheduled_count,
                "total_runs": len(plan.runs),
                "status": "scheduled"
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule experiment {experiment_id}: {e}")
            raise ValueError(f"Cannot schedule experiment: {str(e)}")
    
    async def _queue_run(self, run: RunConfig):
        """Queue a single run for execution"""
        try:
            run_message = {
                "run_id": run.id,
                "experiment_id": run.experiment_id,
                "algorithm_id": run.algorithm_id,
                "benchmark_id": run.benchmark_id,
                "seed": run.seed,
                "budget_type": run.budget_type,
                "budget_value": run.budget_value,
                "metadata": run.metadata,
                "queued_at": datetime.utcnow().isoformat()
            }
            
            if self.message_broker:
                # Send to RabbitMQ
                self.message_broker['channel'].basic_publish(
                    exchange='',
                    routing_key='experiment_runs',
                    body=json.dumps(run_message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Make message persistent
                        timestamp=int(datetime.utcnow().timestamp())
                    )
                )
            else:
                # Fall back to in-memory queue
                self.run_queue.append(run.id)
            
            # Update run status
            await experiment_plan_builder.update_run_status(run.id, RunStatus.PENDING)
            
            logger.debug(f"Queued run {run.id} for execution")
            
        except Exception as e:
            logger.error(f"Failed to queue run {run.id}: {e}")
            raise
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        try:
            if self.message_broker:
                # Get queue info from RabbitMQ
                method = self.message_broker['channel'].queue_declare(
                    queue='experiment_runs', 
                    passive=True
                )
                queue_size = method.method.message_count
            else:
                # Use in-memory queue
                queue_size = len(self.run_queue)
            
            return {
                "queue_size": queue_size,
                "active_runs": len(self.active_runs),
                "max_concurrent": self.max_concurrent_runs,
                "broker_type": "rabbitmq" if self.message_broker else "memory"
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue status: {e}")
            return {"error": str(e)}
    
    async def cancel_experiment_runs(self, experiment_id: str) -> Dict[str, Any]:
        """Cancel all pending/running runs for an experiment"""
        try:
            plan = await experiment_plan_builder.get_plan(experiment_id)
            if not plan:
                return {"error": "Experiment plan not found"}
            
            cancelled_count = 0
            for run in plan.runs:
                if run.status in [RunStatus.PENDING, RunStatus.RUNNING]:
                    await experiment_plan_builder.update_run_status(run.id, RunStatus.CANCELLED)
                    cancelled_count += 1
            
            logger.info(f"Cancelled {cancelled_count} runs for experiment {experiment_id}")
            
            return {
                "experiment_id": experiment_id,
                "cancelled_runs": cancelled_count,
                "status": "cancelled"
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel experiment runs: {e}")
            return {"error": str(e)}
    
    async def handle_run_result(self, run_id: str, result: Dict[str, Any]):
        """Handle completed run result"""
        try:
            # Update run status
            status = RunStatus.COMPLETED if result.get("success") else RunStatus.FAILED
            await experiment_plan_builder.update_run_status(run_id, status)
            
            # Remove from active runs
            if run_id in self.active_runs:
                del self.active_runs[run_id]
            
            logger.info(f"Processed result for run {run_id}: {status}")
            
            # Forward result to tracking service
            await self._forward_result_to_tracking(run_id, result)
            
        except Exception as e:
            logger.error(f"Failed to handle run result for {run_id}: {e}")
    
    async def _forward_result_to_tracking(self, run_id: str, result: Dict[str, Any]):
        """Forward run result to experiment tracking service"""
        try:
            # This would make HTTP request to tracking service
            # For now, just log
            logger.debug(f"Forwarding result for run {run_id} to tracking service")
            # TODO: Implement actual HTTP request to tracking service
            
        except Exception as e:
            logger.error(f"Failed to forward result to tracking: {e}")

# Global instance
run_scheduler = RunScheduler()