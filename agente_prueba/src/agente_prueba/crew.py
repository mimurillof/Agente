# src/latest_ai_development/crew.py
import yaml
from pathlib import Path

def load_config(filename: str) -> dict:
    """Carga la configuración desde un archivo YAML."""
    config_dir = Path(__file__).parent / "config"
    config_path = config_dir / filename
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_agents_config() -> dict:
    """Obtiene la configuración de los agentes."""
    return load_config("agents.yaml")

def get_tasks_config() -> dict:
    """Obtiene la configuración de las tareas."""
    return load_config("tasks.yaml")