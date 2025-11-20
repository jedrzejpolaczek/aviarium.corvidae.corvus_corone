from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import json
import os
import logging
from datetime import datetime
from jinja2 import Template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Report Generator Service",
    description="Generates reports from experiment data",
    version="1.0.0"
)

TRACKING_SERVICE_URL = os.getenv("TRACKING_SERVICE_URL", "http://experiment-tracking:8002")
METRICS_SERVICE_URL = os.getenv("METRICS_SERVICE_URL", "http://metrics-analysis:8005")
PUBLICATION_SERVICE_URL = os.getenv("PUBLICATION_SERVICE_URL", "http://publication-service:8006")

class ReportRequest(BaseModel):
    experiment_ids: List[str]
    title: str = "HPO Experiment Report"
    include_statistical_analysis: bool = True
    include_convergence_plots: bool = True
    format: str = "html"  # html, json

class ReportResponse(BaseModel):
    report_id: str
    title: str
    generated_at: datetime
    format: str
    content: str
    experiments_included: List[str]

# HTML report template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
        .experiment { margin-bottom: 40px; padding: 20px; border: 1px solid #ddd; }
        .metrics { background-color: #f9f9f9; padding: 15px; margin: 10px 0; }
        .comparison { background-color: #e8f4fd; padding: 15px; margin: 20px 0; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .recommendation { background-color: #fffbf0; padding: 10px; margin: 10px 0; border-left: 4px solid #ffa500; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p><strong>Generated:</strong> {{ generated_at }}</p>
        <p><strong>Experiments Analyzed:</strong> {{ experiments|length }}</p>
    </div>
    
    {% for experiment in experiments %}
    <div class="experiment">
        <h2>{{ experiment.name }}</h2>
        <p><strong>ID:</strong> {{ experiment.id }}</p>
        <p><strong>Description:</strong> {{ experiment.description }}</p>
        <p><strong>Status:</strong> {{ experiment.status }}</p>
        <p><strong>Total Runs:</strong> {{ experiment.total_runs }}</p>
        <p><strong>Completed Runs:</strong> {{ experiment.completed_runs }}</p>
        
        {% if experiment.summary %}
        <div class="metrics">
            <h3>Metrics Summary</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Mean</th>
                    <th>Std</th>
                    <th>Min</th>
                    <th>Max</th>
                    <th>Median</th>
                </tr>
                <tr>
                    <td>{{ experiment.summary.metric_name }}</td>
                    <td>{{ "%.6f"|format(experiment.summary.mean) }}</td>
                    <td>{{ "%.6f"|format(experiment.summary.std) }}</td>
                    <td>{{ "%.6f"|format(experiment.summary.min) }}</td>
                    <td>{{ "%.6f"|format(experiment.summary.max) }}</td>
                    <td>{{ "%.6f"|format(experiment.summary.median) }}</td>
                </tr>
            </table>
        </div>
        {% endif %}
    </div>
    {% endfor %}
    
    {% if comparison %}
    <div class="comparison">
        <h2>Statistical Comparison</h2>
        
        <h3>Algorithm Rankings</h3>
        <table>
            <tr>
                <th>Rank</th>
                <th>Algorithm</th>
                <th>Median Performance</th>
                <th>Mean Performance</th>
            </tr>
            {% for ranking in comparison.rankings %}
            <tr>
                <td>{{ ranking.rank }}</td>
                <td>{{ ranking.algorithm }}</td>
                <td>{{ "%.6f"|format(ranking.median_performance) }}</td>
                <td>{{ "%.6f"|format(ranking.mean_performance) }}</td>
            </tr>
            {% endfor %}
        </table>
        
        {% if comparison.statistical_tests.kruskal_wallis %}
        <h3>Statistical Tests</h3>
        <p><strong>Kruskal-Wallis Test:</strong></p>
        <ul>
            <li>Statistic: {{ "%.4f"|format(comparison.statistical_tests.kruskal_wallis.statistic) }}</li>
            <li>P-value: {{ "%.6f"|format(comparison.statistical_tests.kruskal_wallis.p_value) }}</li>
            <li>Significant: {{ comparison.statistical_tests.kruskal_wallis.significant }}</li>
        </ul>
        {% endif %}
        
        <h3>Recommendations</h3>
        {% for recommendation in comparison.recommendations %}
        <div class="recommendation">
            {{ recommendation }}
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    <div class="footer">
        <p><em>Report generated by Corvus Corone HPO Benchmarking Platform</em></p>
    </div>
</body>
</html>
"""

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "report-generator"}

@app.post("/api/reports/generate", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """Generate comprehensive report from experiment data"""
    report_id = f"report_{int(datetime.utcnow().timestamp())}"
    
    try:
        # Collect experiment data
        experiments_data = []
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            for exp_id in request.experiment_ids:
                # Get experiment details
                exp_response = await client.get(f"{TRACKING_SERVICE_URL}/api/tracking/experiments/{exp_id}")
                if exp_response.status_code == 200:
                    experiment = exp_response.json()
                    
                    # Get metrics summary
                    summary_response = await client.get(f"{METRICS_SERVICE_URL}/api/metrics/experiments/{exp_id}/summary")
                    if summary_response.status_code == 200:
                        experiment["summary"] = summary_response.json()
                    
                    experiments_data.append(experiment)
        
        if not experiments_data:
            raise HTTPException(status_code=404, detail="No valid experiments found")
        
        # Generate comparison if multiple experiments
        comparison_data = None
        if len(request.experiment_ids) > 1 and request.include_statistical_analysis:
            async with httpx.AsyncClient(timeout=60.0) as client:
                comparison_response = await client.post(
                    f"{METRICS_SERVICE_URL}/api/metrics/compare",
                    json={
                        "experiment_ids": request.experiment_ids,
                        "metric_name": "objective",
                        "confidence_level": 0.95
                    }
                )
                if comparison_response.status_code == 200:
                    comparison_data = comparison_response.json()
        
        # Generate report content based on format
        if request.format == "html":
            template = Template(HTML_TEMPLATE)
            content = template.render(
                title=request.title,
                generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                experiments=experiments_data,
                comparison=comparison_data
            )
        elif request.format == "json":
            content = json.dumps({
                "title": request.title,
                "generated_at": datetime.utcnow().isoformat(),
                "experiments": experiments_data,
                "comparison": comparison_data
            }, indent=2)
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
        return ReportResponse(
            report_id=report_id,
            title=request.title,
            generated_at=datetime.utcnow(),
            format=request.format,
            content=content,
            experiments_included=request.experiment_ids
        )
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/api/reports/templates")
async def list_report_templates():
    """List available report templates"""
    return {
        "templates": [
            {
                "id": "experiment_summary",
                "name": "Experiment Summary Report",
                "description": "Basic summary of experiment results",
                "formats": ["html", "json"]
            },
            {
                "id": "algorithm_comparison",
                "name": "Algorithm Comparison Report",
                "description": "Statistical comparison of multiple algorithms",
                "formats": ["html", "json"]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)