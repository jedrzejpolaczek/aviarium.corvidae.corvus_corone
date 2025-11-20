from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import numpy as np
import scipy.stats as stats
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Metrics Analysis Service",
    description="Statistical analysis and comparison of HPO experiment results",
    version="1.0.0"
)

TRACKING_SERVICE_URL = os.getenv("TRACKING_SERVICE_URL", "http://experiment-tracking:8002")

class MetricSummary(BaseModel):
    metric_name: str
    count: int
    mean: float
    std: float
    min: float
    max: float
    median: float
    q25: float
    q75: float

class ComparisonRequest(BaseModel):
    experiment_ids: List[str]
    metric_name: str = "objective"
    confidence_level: float = 0.95

class ComparisonResult(BaseModel):
    metric_name: str
    algorithms: List[str]
    summary_stats: List[MetricSummary]
    statistical_tests: Dict[str, Any]
    rankings: List[Dict[str, Any]]
    recommendations: List[str]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "metrics-analysis"}

@app.get("/api/metrics/experiments/{experiment_id}/summary")
async def get_experiment_summary(experiment_id: str, metric_name: str = "objective"):
    """Get statistical summary of experiment metrics"""
    async with httpx.AsyncClient() as client:
        # Get all runs for experiment
        response = await client.get(f"{TRACKING_SERVICE_URL}/api/tracking/experiments/{experiment_id}/runs")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        runs = response.json()
        
        # Collect metrics for all runs
        all_values = []
        for run in runs:
            if run["status"] == "completed":
                metric_response = await client.get(f"{TRACKING_SERVICE_URL}/api/tracking/runs/{run['id']}/metrics")
                if metric_response.status_code == 200:
                    metrics = metric_response.json()
                    # Get final value of specified metric
                    target_metrics = [m for m in metrics if m["name"] == metric_name]
                    if target_metrics:
                        final_metric = max(target_metrics, key=lambda x: x["step"])
                        all_values.append(final_metric["value"])
        
        if not all_values:
            raise HTTPException(status_code=404, detail="No metrics found")
        
        # Calculate statistics
        values_array = np.array(all_values)
        summary = MetricSummary(
            metric_name=metric_name,
            count=len(all_values),
            mean=float(np.mean(values_array)),
            std=float(np.std(values_array)),
            min=float(np.min(values_array)),
            max=float(np.max(values_array)),
            median=float(np.median(values_array)),
            q25=float(np.percentile(values_array, 25)),
            q75=float(np.percentile(values_array, 75))
        )
        
        return summary

@app.post("/api/metrics/compare", response_model=ComparisonResult)
async def compare_experiments(comparison: ComparisonRequest):
    """Compare results across multiple experiments"""
    experiment_data = {}
    
    async with httpx.AsyncClient() as client:
        # Collect data for each experiment
        for exp_id in comparison.experiment_ids:
            # Get experiment info
            exp_response = await client.get(f"{TRACKING_SERVICE_URL}/api/tracking/experiments/{exp_id}")
            if exp_response.status_code != 200:
                continue
            
            experiment = exp_response.json()
            
            # Get runs
            runs_response = await client.get(f"{TRACKING_SERVICE_URL}/api/tracking/experiments/{exp_id}/runs")
            if runs_response.status_code != 200:
                continue
            
            runs = runs_response.json()
            
            # Extract metric values
            values = []
            for run in runs:
                if run["status"] == "completed":
                    metrics_response = await client.get(f"{TRACKING_SERVICE_URL}/api/tracking/runs/{run['id']}/metrics")
                    if metrics_response.status_code == 200:
                        metrics = metrics_response.json()
                        target_metrics = [m for m in metrics if m["name"] == comparison.metric_name]
                        if target_metrics:
                            final_metric = max(target_metrics, key=lambda x: x["step"])
                            values.append(final_metric["value"])
            
            if values:
                experiment_data[exp_id] = {
                    "name": experiment["name"],
                    "values": values,
                    "config": experiment.get("config_json", {})
                }
    
    if len(experiment_data) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 experiments with data")
    
    # Calculate summary statistics for each experiment
    summary_stats = []
    algorithms = []
    values_by_exp = []
    
    for exp_id, data in experiment_data.items():
        values_array = np.array(data["values"])
        summary = MetricSummary(
            metric_name=comparison.metric_name,
            count=len(data["values"]),
            mean=float(np.mean(values_array)),
            std=float(np.std(values_array)),
            min=float(np.min(values_array)),
            max=float(np.max(values_array)),
            median=float(np.median(values_array)),
            q25=float(np.percentile(values_array, 25)),
            q75=float(np.percentile(values_array, 75))
        )
        summary_stats.append(summary)
        algorithms.append(data["name"])
        values_by_exp.append(data["values"])
    
    # Statistical tests
    statistical_tests = {}
    
    # Kruskal-Wallis test (non-parametric ANOVA)
    if len(values_by_exp) > 2:
        kw_stat, kw_pvalue = stats.kruskal(*values_by_exp)
        statistical_tests["kruskal_wallis"] = {
            "statistic": float(kw_stat),
            "p_value": float(kw_pvalue),
            "significant": kw_pvalue < (1 - comparison.confidence_level)
        }
    
    # Pairwise Mann-Whitney U tests
    pairwise_tests = []
    for i in range(len(values_by_exp)):
        for j in range(i + 1, len(values_by_exp)):
            u_stat, u_pvalue = stats.mannwhitneyu(values_by_exp[i], values_by_exp[j], alternative='two-sided')
            pairwise_tests.append({
                "algorithm_1": algorithms[i],
                "algorithm_2": algorithms[j],
                "statistic": float(u_stat),
                "p_value": float(u_pvalue),
                "significant": u_pvalue < (1 - comparison.confidence_level)
            })
    
    statistical_tests["pairwise_tests"] = pairwise_tests
    
    # Rankings (by median performance)
    rankings = []
    for i, summary in enumerate(summary_stats):
        rankings.append({
            "algorithm": algorithms[i],
            "median_performance": summary.median,
            "mean_performance": summary.mean,
            "rank": 0  # Will be filled below
        })
    
    # Sort by median and assign ranks
    rankings.sort(key=lambda x: x["median_performance"])
    for i, ranking in enumerate(rankings):
        ranking["rank"] = i + 1
    
    # Generate recommendations
    recommendations = []
    
    best_algorithm = rankings[0]["algorithm"]
    recommendations.append(f"Best performing algorithm: {best_algorithm}")
    
    if statistical_tests.get("kruskal_wallis", {}).get("significant", False):
        recommendations.append("Statistically significant differences found between algorithms")
    else:
        recommendations.append("No statistically significant differences found between algorithms")
    
    # Check for large effect sizes
    for test in pairwise_tests:
        if test["significant"] and test["p_value"] < 0.01:
            recommendations.append(
                f"Strong evidence that {test['algorithm_1']} and {test['algorithm_2']} perform differently"
            )
    
    return ComparisonResult(
        metric_name=comparison.metric_name,
        algorithms=algorithms,
        summary_stats=summary_stats,
        statistical_tests=statistical_tests,
        rankings=rankings,
        recommendations=recommendations
    )

@app.get("/api/metrics/experiments/{experiment_id}/convergence")
async def get_convergence_data(experiment_id: str, metric_name: str = "best_so_far"):
    """Get convergence data for experiment visualization"""
    async with httpx.AsyncClient() as client:
        # Get all runs for experiment
        response = await client.get(f"{TRACKING_SERVICE_URL}/api/tracking/experiments/{experiment_id}/runs")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        runs = response.json()
        
        convergence_data = []
        for run in runs:
            if run["status"] == "completed":
                metrics_response = await client.get(f"{TRACKING_SERVICE_URL}/api/tracking/runs/{run['id']}/metrics")
                if metrics_response.status_code == 200:
                    metrics = metrics_response.json()
                    # Get convergence metrics
                    convergence_metrics = [m for m in metrics if m["name"] == metric_name]
                    if convergence_metrics:
                        convergence_metrics.sort(key=lambda x: x["step"])
                        convergence_data.append({
                            "run_id": run["id"],
                            "algorithm": run["algorithm_version_id"],
                            "steps": [m["step"] for m in convergence_metrics],
                            "values": [m["value"] for m in convergence_metrics]
                        })
        
        return {"convergence_data": convergence_data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)