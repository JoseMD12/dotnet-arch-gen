import json
import os
from typing import Dict, List, TypedDict, Optional
from .ui import err

class LayerInfo(TypedDict):
    template: str
    subdirs: List[str]
    deps: List[str]
    name: Optional[str] # Nome customizado para a camada (ex: API em vez de Api)

DEFAULT_LAYER_CONFIG: Dict[str, LayerInfo] = {
    "domain": {
        "template": "classlib",
        "subdirs": ["Entities", "ValueObjects", "Exceptions", "Repositories"],
        "deps": [],
        "name": "Domain"
    },
    "application": {
        "template": "classlib",
        "subdirs": ["UseCases", "DTOs", "Interfaces", "Mappings"],
        "deps": ["domain"],
        "name": "Application"
    },
    "infrastructure": {
        "template": "classlib",
        "subdirs": ["Data", "Repositories", "Security", "Migrations"],
        "deps": ["domain"],
        "name": "Infrastructure"
    },
    "api": {
        "template": "webapi",
        "subdirs": ["Controllers", "Endpoints", "Middlewares"],
        "deps": ["application", "infrastructure"],
        "name": "API"
    },
    "worker": {
        "template": "worker",
        "subdirs": ["Jobs", "Handlers", "Consumers"],
        "deps": ["application", "infrastructure"],
        "name": "Worker"
    },
    "console": {
        "template": "console",
        "subdirs": ["Commands", "Handlers"],
        "deps": ["application"],
        "name": "Console"
    },
    "tests": {
        "template": "xunit",
        "subdirs": ["Unit", "Integration", "Fixtures"],
        "deps": ["application", "infrastructure"],
        "name": "Tests"
    }
}

def load_config(config_path: str):
    if not os.path.exists(config_path):
        err(f"Arquivo não encontrado: {config_path}")

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        config["_layer_config"] = DEFAULT_LAYER_CONFIG.copy()
        return config
    except Exception as e:
        err(f"Erro ao ler JSON: {e}")
