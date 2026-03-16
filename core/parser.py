from typing import Dict, Tuple, List


def parse_k_file(file_path: str) -> Tuple[
    Dict[int, Tuple[float, float, float]],
    Dict[int, Dict[str, List[int]]]
]:
    nodes: Dict[int, Tuple[float, float, float]] = {}
    elements: Dict[int, Dict[str, List[int]]] = {}

    parsing_nodes = False
    parsing_elements = False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
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