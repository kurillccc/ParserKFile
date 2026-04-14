from dataclasses import dataclass


@dataclass
class ProcessingConfig:
    yaml_file: str
    subregion: int
    density: float
    pr: float
    coordinate: str
    heterogeneous_layer: bool
