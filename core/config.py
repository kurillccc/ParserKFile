from dataclasses import dataclass


@dataclass
class ProcessingConfig:
    k_file: str
    cd_file: str
    subregion: int
    density: float
    pr: float
    coordinate: str
    heterogeneous_layer: bool
