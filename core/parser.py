import yaml
import os
from typing import Dict, Tuple, List


def parse_k_file(file_path: str, on_progress=None) -> Tuple[
    Dict[int, Tuple[float, float, float]],
    Dict[int, Dict[str, List[int]]]
]:
    nodes: Dict[int, Tuple[float, float, float]] = {}
    elements: Dict[int, Dict[str, List[int]]] = {}

    parsing_nodes = False
    parsing_elements = False

    # Подсчёт строк для прогресса
    total_lines = 0
    if on_progress:
        with open(file_path, "rb") as f:
            total_lines = sum(1 for _ in f)

    current_line = 0
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            current_line += 1
            if on_progress and total_lines > 0:
                progress = 10 + int((current_line / total_lines) * 25)  # 10-35%
                if current_line % max(1, total_lines // 20) == 0:  # каждые 5%
                    on_progress(progress, "Парсинг K-файла...")

            
            line = line.rstrip()
            if not line:
                continue

            if line.startswith("*NODE"):
                parsing_nodes = True
                parsing_elements = False
                continue

            if line.startswith("*ELEMENT_SOLID"):
                parsing_nodes = False
                parsing_elements = True
                continue

            if line.startswith("*END"):
                parsing_nodes = False
                parsing_elements = False
                continue

            if parsing_nodes:
                p = line.split(",")
                node_id = int(p[0])
                nodes[node_id] = (float(p[1]), float(p[2]), float(p[3]))

            elif parsing_elements:
                p = line.split(",")
                element_id = int(p[0])
                elements[element_id] = {
                    "subregion": int(p[1]),
                    "nodes": list(map(int, p[2:]))
                }

    if not nodes:
        print("*NODE не найден")
    if not elements:
        print("*ELEMENT_SOLID не найден")

    return nodes, elements


def parse_yaml_file(file_path: str) -> Tuple[str, str]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict):
            raise ValueError("YAML файл должен содержать объект (key-value)")

        try:
            mesh_name = data["MESH"]
            cd_name = data["COMMON_DATA"]
        except KeyError as e:
            raise ValueError(f"В YAML отсутствует обязательный ключ: {e.args[0]}") from e

        base_dir = os.path.dirname(file_path)

        mesh_path = os.path.join(base_dir, mesh_name)
        cd_path = os.path.join(base_dir, cd_name)

        return mesh_path, cd_path

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Файл не найден: {file_path}") from e

    except yaml.YAMLError as e:
        raise ValueError(f"Ошибка парсинга YAML в файле {file_path}") from e