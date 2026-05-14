import json
import os
from typing import Dict, List, TypedDict
from .ui import err

class LayerInfo(TypedDict):
    template: str
    subdirs: List[str]
    deps: List[str]

DEFAULT_LAYER_CONFIG: Dict[str, LayerInfo] = {
    "domain": {
        "template": "classlib",
        "subdirs": ["Entities", "ValueObjects", "Exceptions", "Repositories"],
        "deps": []
    },
    "application": {
        "template": "classlib",
        "subdirs": ["UseCases", "DTOs", "Interfaces", "Mappings"],
        "deps": ["domain"]
    },
    "infrastructure": {
        "template": "classlib",
        "subdirs": ["Data", "Repositories", "Security", "Migrations"],
        "deps": ["domain"]
    },
    "api": {
        "template": "webapi",
        "subdirs": ["Controllers", "Endpoints", "Middlewares"],
        "deps": ["application", "infrastructure"]
    },
    "worker": {
        "template": "worker",
        "subdirs": ["Jobs", "Handlers", "Consumers"],
        "deps": ["application", "infrastructure"]
    },
    "console": {
        "template": "console",
        "subdirs": ["Commands", "Handlers"],
        "deps": ["application"]
    },
    "tests": {
        "template": "xunit",
        "subdirs": ["Unit", "Integration", "Fixtures"],
        "deps": ["application", "infrastructure"]
    }
}

def load_config(config_path: str):
    if not os.path.exists(config_path):
        err(f"Arquivo não encontrado: {config_path}")

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # Mesclar camadas customizadas se existirem
        layer_config = DEFAULT_LAYER_CONFIG.copy()
        if "custom_layers" in config:
            layer_config.update(config["custom_layers"])
        
        config["_layer_config"] = layer_config
        return config
    except Exception as e:
        err(f"Erro ao ler JSON: {e}")
