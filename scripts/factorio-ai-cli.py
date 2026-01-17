#!/usr/bin/env python3
"""
Factorio AI CLI - Unified command-line interface
Replaces all scattered scripts with one simple tool
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import track
from pathlib import Path
import subprocess
import sys

app = typer.Typer(
    name="factorio-ai", help="🎮 Factorio AI Training & Management Tool", add_completion=False
)
console = Console()

# Sub-commands
train_app = typer.Typer(help="🎯 Training commands")
data_app = typer.Typer(help="📚 Dataset commands")
model_app = typer.Typer(help="🤖 Model commands")
system_app = typer.Typer(help="⚙️  System commands")

app.add_typer(train_app, name="train")
app.add_typer(data_app, name="data")
app.add_typer(model_app, name="model")
app.add_typer(system_app, name="system")

# ============================================================================
# TRAINING COMMANDS
# ============================================================================


@train_app.command("start")
def train_start(
    model: str = "qwen-1.5b", iters: int = 1000, batch_size: int = 4, learning_rate: float = 1e-5
):
    """Start model fine-tuning"""
    console.print(f"🚀 Starting training: {model}", style="bold green")

    model_path = f"models/{model}-4bit" if "qwen" in model else f"models/{model}"

    cmd = [
        "python",
        "-m",
        "mlx_lm",
        "lora",
        "--model",
        model_path,
        "--data",
        "training_data",
        "--train",
        "--batch-size",
        str(batch_size),
        "--num-layers",
        "16",
        "--iters",
        str(iters),
        "--learning-rate",
        str(learning_rate),
        "--val-batches",
        "25",
        "--save-every",
        "100",
    ]

    subprocess.run(cmd)


@train_app.command("continue")
def train_continue(iters: int = 500):
    """Continue training from last checkpoint"""
    console.print(f"♻️  Continuing training for {iters} more iterations", style="bold cyan")

    # Find latest adapter
    adapters_dir = Path("adapters")
    if not adapters_dir.exists():
        console.print("❌ No adapters found. Start training first!", style="red")
        return

    latest = adapters_dir / "adapters.safetensors"
    if not latest.exists():
        console.print("❌ No checkpoints found!", style="red")
        return

    cmd = [
        sys.executable,
        "-m",
        "mlx_lm",
        "lora",
        "--model",
        "models/qwen-1.5b-4bit",
        "--resume-adapter-file",
        str(latest),
        "--data",
        "training_data",
        "--train",
        "--iters",
        str(iters),
    ]

    subprocess.run(cmd)


@train_app.command("test")
def train_test(prompt: str = typer.Argument("Generate Factorio code to harvest iron ore")):
    """Test the trained model"""
    console.print(f"🧪 Testing model with prompt: {prompt}", style="bold magenta")

    cmd = [
        sys.executable,
        "-m",
        "mlx_lm",
        "generate",
        "--model",
        "models/qwen-1.5b-4bit",
        "--adapter-path",
        "adapters",
        "--prompt",
        prompt,
        "--max-tokens",
        "200",
    ]

    subprocess.run(cmd)


# ============================================================================
# DATA COMMANDS
# ============================================================================


@data_app.command("collect")
def data_collect():
    """Collect all datasets from sources"""
    console.print("📥 Collecting datasets from all sources...", style="bold blue")

    scripts = [
        "scripts/download_huggingface_datasets.py",
        "scripts/scrape_wiki.py",
        "scripts/generate_variations.py",
    ]

    for script in track(scripts, description="Running collectors..."):
        if Path(script).exists():
            subprocess.run([sys.executable, script])


@data_app.command("clean")
def data_clean():
    """Clean and deduplicate datasets"""
    console.print("🧹 Cleaning and deduplicating data...", style="bold yellow")
    subprocess.run([sys.executable, "scripts/clean_and_deduplicate.py"])


@data_app.command("stats")
def data_stats():
    """Show dataset statistics"""
    console.print("📊 Dataset Statistics", style="bold")

    table = Table(show_header=True)
    table.add_column("File", style="cyan")
    table.add_column("Examples", justify="right", style="green")
    table.add_column("Size", justify="right", style="yellow")

    data_dir = Path("training_data")
    for file in data_dir.glob("*.jsonl"):
        if file.name.startswith("._"):  # Skip MacOS hidden files
            continue
        try:
            count = sum(1 for _ in open(file))
            size = file.stat().st_size / 1024 / 1024  # MB
            table.add_row(file.name, str(count), f"{size:.1f} MB")
        except Exception:
            pass

    console.print(table)


# ============================================================================
# MODEL COMMANDS
# ============================================================================


@model_app.command("list")
def model_list():
    """List available models"""
    console.print("🤖 Available Models", style="bold")

    models_dir = Path("models")
    if not models_dir.exists():
        console.print("No models found", style="dim")
        return

    table = Table(show_header=True)
    table.add_column("Model", style="cyan")
    table.add_column("Size", justify="right", style="yellow")

    for model_dir in models_dir.iterdir():
        if model_dir.is_dir():
            size = sum(f.stat().st_size for f in model_dir.rglob("*") if f.is_file())
            size_gb = size / 1024 / 1024 / 1024
            table.add_row(model_dir.name, f"{size_gb:.2f} GB")

    console.print(table)


@model_app.command("download")
def model_download(name: str = "qwen-1.5b"):
    """Download a model"""
    console.print(f"📥 Downloading {name}...", style="bold green")

    if "qwen" in name.lower():
        subprocess.run([sys.executable, "scripts/download_qwen.py"])
    else:
        console.print(f"❌ Model {name} not supported yet", style="red")


@model_app.command("clean")
def model_clean():
    """Clean old models"""
    subprocess.run(["./scripts/cleanup_models.sh"])


# ============================================================================
# SYSTEM COMMANDS
# ============================================================================


@system_app.command("info")
def system_info():
    """Show system information"""
    console.print("💻 System Information", style="bold")

    import platform
    import psutil

    table = Table(show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("OS", f"{platform.system()} {platform.release()}")
    table.add_row("Python", platform.python_version())
    table.add_row("CPU", platform.processor())
    table.add_row("RAM", f"{psutil.virtual_memory().total / 1024**3:.1f} GB")
    table.add_row("RAM Available", f"{psutil.virtual_memory().available / 1024**3:.1f} GB")

    # Disk space
    disk = psutil.disk_usage("/")
    table.add_row("Disk Total", f"{disk.total / 1024**3:.1f} GB")
    table.add_row("Disk Free", f"{disk.free / 1024**3:.1f} GB")
    table.add_row("Disk Used", f"{disk.percent}%")

    console.print(table)


@system_app.command("cleanup")
def system_cleanup():
    """Clean system caches and temporary files"""
    console.print("🧹 Cleaning system...", style="bold yellow")
    subprocess.run(["./scripts/cleanup_disk_space.sh"])


@system_app.command("mlflow")
def system_mlflow():
    """Launch MLflow UI"""
    console.print("🚀 Launching MLflow UI at http://localhost:5000", style="bold green")
    subprocess.run(["mlflow", "ui", "--port", "5000"])


# ============================================================================
# MAIN COMMAND
# ============================================================================


@app.command()
def status():
    """Show project status"""
    console.print("\n🎮 Factorio AI Project Status\n", style="bold green")

    # Models
    console.print("Models:", style="bold cyan")
    models_dir = Path("models")
    if models_dir.exists():
        for m in models_dir.iterdir():
            if m.is_dir():
                console.print(f"  ✓ {m.name}", style="green")

    # Datasets
    console.print("\nDatasets:", style="bold cyan")
    data_dir = Path("training_data")
    if data_dir.exists():
        for f in data_dir.glob("*.jsonl"):
            if f.name.startswith("._"):  # Skip MacOS hidden files
                continue
            try:
                count = sum(1 for _ in open(f))
                console.print(f"  ✓ {f.name}: {count} examples", style="green")
            except Exception:
                pass

    # Adapters
    console.print("\nAdapters:", style="bold cyan")
    adapters_dir = Path("adapters")
    if adapters_dir.exists() and list(adapters_dir.glob("*.safetensors")):
        for a in adapters_dir.glob("*.safetensors"):
            console.print(f"  ✓ {a.name}", style="green")
    else:
        console.print("  No adapters yet", style="dim")


if __name__ == "__main__":
    app()
