import json
import os
from typing import Dict, List, Optional, Literal, Set
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from .ui import err

# --- Tipos e Literais ---
ValidFramework = Literal["net8.0", "net9.0", "net10.0"]
ValidLayer = Literal["domain", "application", "infrastructure", "api", "worker", "console", "tests"]

IDENTIFIER_REGEX = r"^[a-zA-Z][a-zA-Z0-9._-]{0,99}$"

class LayerInfo(BaseModel):
    template: str
    subdirs: List[str]
    deps: List[ValidLayer]
    name: Optional[str] = None

DEFAULT_LAYER_CONFIG: Dict[ValidLayer, LayerInfo] = {
    "domain": LayerInfo(
        template="classlib",
        subdirs=["Entities", "ValueObjects", "Exceptions", "Repositories"],
        deps=[],
        name="Domain"
    ),
    "application": LayerInfo(
        template="classlib",
        subdirs=["UseCases", "DTOs", "Interfaces", "Mappings"],
        deps=["domain"],
        name="Application"
    ),
    "infrastructure": LayerInfo(
        template="classlib",
        subdirs=["Data", "Repositories", "Security"],
        deps=["domain"],
        name="Infrastructure"
    ),
    "api": LayerInfo(
        template="webapi",
        subdirs=["Controllers", "Endpoints", "Middlewares"],
        deps=["application", "infrastructure"],
        name="API"
    ),
    "worker": LayerInfo(
        template="worker",
        subdirs=["Jobs", "Handlers", "Consumers"],
        deps=["application", "infrastructure"],
        name="Worker"
    ),
    "console": LayerInfo(
        template="console",
        subdirs=["Commands", "Handlers"],
        deps=["application"],
        name="Console"
    ),
    "tests": LayerInfo(
        template="xunit",
        subdirs=["Unit", "Integration", "Fixtures"],
        deps=["application", "infrastructure"],
        name="Tests"
    )
}

# --- Modelos de Configuração ---

class ModuleConfig(BaseModel):
    name: str = Field(pattern=IDENTIFIER_REGEX)
    layers: List[ValidLayer]

class SharedConfig(BaseModel):
    layers: List[ValidLayer] = Field(default_factory=list)

class ProjectConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    solution: str = Field(pattern=IDENTIFIER_REGEX)
    namespace: str = Field(pattern=IDENTIFIER_REGEX)
    framework: ValidFramework = "net10.0"
    output_path: Optional[str] = None
    docker: bool = False
    gitignore: bool = True
    shared: SharedConfig = Field(default_factory=SharedConfig)
    modules: List[ModuleConfig] = Field(default_factory=list)
    
    @property
    def layer_definitions(self) -> Dict[ValidLayer, LayerInfo]:
        return DEFAULT_LAYER_CONFIG

    @field_validator("output_path")
    @classmethod
    def validate_no_path_traversal(cls, v: Optional[str]) -> Optional[str]:
        if v and ".." in v:
            raise ValueError("O campo 'output_path' não pode conter sequências de path traversal (..)")
        return v

    @model_validator(mode="after")
    def validate_unique_modules(self) -> "ProjectConfig":
        names: Set[str] = set()
        for module in self.modules:
            if module.name in names:
                raise ValueError(f"Nome de módulo duplicado: {module.name}")
            names.add(module.name)
        return self

def load_config(config_path: str) -> ProjectConfig:
    if not os.path.exists(config_path):
        err(f"Arquivo não encontrado: {config_path}")

    try:
        with open(config_path, "r") as f:
            data = json.load(f)
        
        return ProjectConfig.model_validate(data)
    except Exception as e:
        err(f"Erro de validação no arquivo '{config_path}':\n{e}")
