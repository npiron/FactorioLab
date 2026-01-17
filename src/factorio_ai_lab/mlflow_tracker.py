"""
MLflow tracking wrapper for Factorio AI fine-tuning
Automatically logs metrics, parameters, and artifacts
"""

import mlflow
import mlflow.pytorch
from pathlib import Path
from datetime import datetime


from typing import Optional, Dict, Any, Union


class FactorioMLflowTracker:
    def __init__(self, experiment_name: str = "factorio-ai") -> None:
        """Initialize MLflow tracking"""
        # Setup MLflow
        mlflow.set_tracking_uri("file:./mlruns")
        mlflow.set_experiment(experiment_name)

    def start_run(
        self, run_name: Optional[str] = None, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Start a new MLflow run"""
        if run_name is None:
            run_name = f"train-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        mlflow.start_run(run_name=run_name)

        # Log parameters
        if params:
            mlflow.log_params(params)

        return mlflow.active_run()

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        """Log training metrics"""
        mlflow.log_metrics(metrics, step=step)

    def log_dataset_stats(self, train_path: str, valid_path: str) -> None:
        """Log dataset statistics"""
        # Count examples
        train_count = sum(1 for _ in open(train_path))
        valid_count = sum(1 for _ in open(valid_path))

        mlflow.log_params(
            {
                "train_examples": train_count,
                "valid_examples": valid_count,
                "total_examples": train_count + valid_count,
            }
        )

    def log_model(
        self, model_path: Union[str, Path], adapter_path: Optional[Union[str, Path]] = None
    ) -> None:
        """Log the trained model"""
        # Log model directory
        mlflow.log_artifacts(str(model_path), artifact_path="model")

        # Log adapters if available
        if adapter_path and Path(adapter_path).exists():
            mlflow.log_artifacts(str(adapter_path), artifact_path="adapters")

    def end_run(self) -> None:
        """End current MLflow run"""
        mlflow.end_run()

    def get_best_run(self, metric: str = "val_loss") -> Any:
        """Get the run with best metric"""
        experiment = mlflow.get_experiment_by_name("factorio-ai")
        runs = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=[f"metrics.{metric} ASC"],
            max_results=1,
        )
        return runs.iloc[0] if len(runs) > 0 else None


def launch_mlflow_ui() -> None:
    """Launch MLflow UI"""
    import subprocess

    print("🚀 Launching MLflow UI...")
    print("   Visit: http://localhost:5000")
    subprocess.Popen(["mlflow", "ui", "--port", "5000"])


if __name__ == "__main__":
    # Example usage
    tracker = FactorioMLflowTracker()

    # Start a run
    tracker.start_run(
        run_name="test-run",
        params={"model": "qwen-1.5b", "batch_size": 4, "learning_rate": 1e-5, "iters": 1000},
    )

    # Log some metrics
    tracker.log_metrics({"train_loss": 3.5, "val_loss": 3.8}, step=0)
    tracker.log_metrics({"train_loss": 2.1, "val_loss": 2.3}, step=100)

    # End run
    tracker.end_run()

    print("✅ Example run logged!")
    print("   Run: mlflow ui --port 5000")
    print("   Then visit: http://localhost:5000")
