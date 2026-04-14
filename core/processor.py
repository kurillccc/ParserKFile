from typing import Dict, Tuple, List
from collections import Counter


def filter_elements_by_subregion(elements: Dict[int, Dict[str, List[int]]], target_subregion: int) -> Dict[
    int, List[int]]:
    """Фильтрует элементы, оставляя только те, что принадлежат заданной подобласти."""
    return {
        element_id: data["nodes"]
        for element_id, data in elements.items()
        if data["subregion"] == target_subregion
    }

 
def group_nodes_by_coordinate(
        nodes: Dict[int, Tuple[float, float, float]],
        coordinate: str
) -> Dict[float, List[int]]:

    axis_map = {"X": 0, "Y": 1, "Z": 2}
    try:
        axis = axis_map[coordinate]
    except KeyError:
        raise ValueError("Некорректная координата. Используйте 'X', 'Y' или 'Z'.")

    grouped_nodes: Dict[float, List[int]] = {}

    for node_id, coords in nodes.items():
        coord_value = coords[axis]
        grouped_nodes.setdefault(coord_value, []).append(node_id)

    return grouped_nodes


def find_h_and_home(
        nodes: Dict[int, Tuple[float, float, float]],
        coordinate: str
) -> Tuple[
    float,
    Dict[int, Tuple[float, float, float]],
    List[Tuple[int, Tuple[float, float, float]]]
]:

    max_x = max_y = max_z = 0.0

    # --- первый проход: ищем габариты дома ---
    for x, y, z in nodes.values():
        if y == 0.0 and z == 0.0:
            if x > max_x:
                max_x = x
        if x == 0.0 and z == 0.0:
            if y > max_y:
                max_y = y
        if x == 0.0 and y == 0.0:
            if z > max_z:
                max_z = z

    axis_map = {
        'X': (max_x, max_y, max_z),
        'Y': (max_y, max_x, max_z),
        'Z': (max_z, max_x, max_y),
    }

    try:
        h, a, b = axis_map[coordinate]
    except KeyError:
        raise ValueError("Некорректная координата. Используйте 'X', 'Y' или 'Z'.")

    # --- второй проход: фильтрация узлов ---
    filtered_nodes = {}
    nodes_outside = []

    for node_id, (x, y, z) in nodes.items():
        if x <= a and y <= b and z <= h:
            filtered_nodes[node_id] = (x, y, z)
        else:
            nodes_outside.append((node_id, (x, y, z)))

    return h, filtered_nodes, nodes_outside


def find_elements_for_layer(
    nodes: Dict[int, Tuple[float, float, float]],
    elements: Dict[int, List[int]],
    coordinate: str,
    heterogeneous_layer: bool,
    on_progress=None
) -> Dict[float, List[int]]:
    
    coord_idx = {'x': 0, 'y': 1, 'z': 2}[coordinate.lower()]
    tolerance: float = 0.7625 if heterogeneous_layer else 1e-9
    
    node_to_layer: Dict[int, float] = {}
    layer_nodes: Dict[float, List[int]] = {}

    if on_progress:
        on_progress(53, "Формирование слоёв...")
    
    sorted_nodes = sorted(nodes.items(), key=lambda item: item[1][coord_idx])

    if on_progress:
        on_progress(56, "Формирование слоёв...")
    
    for node_id, coords in sorted_nodes:
        coord_value = coords[coord_idx]
        
        found_layer = None
        min_diff = float('inf')
        
        for layer_coord in layer_nodes.keys():
            diff = abs(coord_value - layer_coord)
            if diff <= tolerance:
                if diff < min_diff:
                    found_layer = layer_coord
                    min_diff = diff
        
        if found_layer is not None:
            node_to_layer[node_id] = found_layer
            layer_nodes[found_layer].append(node_id)
        else:
            rounded_coord = round(coord_value / tolerance) * tolerance
            node_to_layer[node_id] = rounded_coord
            layer_nodes[rounded_coord] = [node_id]

    if on_progress:
        on_progress(60, f"Формирование слоёв...")
    
    layer_elements: Dict[float, List[int]] = {}
    processed_elements = set()
    
    elements_items = list(elements.items())
    total_layers = len(layer_nodes)

    if on_progress:
        on_progress(64, "Формирование слоёв...")
    
    for idx, (layer_coord, node_ids) in enumerate(layer_nodes.items()):
        if on_progress and total_layers > 0:
            progress = 68 + int((idx / total_layers) * 5)  # 68-73%
            if idx % max(1, total_layers // 10) == 0:  # каждые 10% слоёв
                on_progress(progress, f"Обработка слоя {idx+1}/{total_layers}")
        
        node_ids_set = set(node_ids)
        elements_in_layer = []
        
        for element_id, element_nodes in elements_items:
            if element_id in processed_elements:
                continue
            
            for nid in element_nodes:
                if nid in node_ids_set:
                    elements_in_layer.append(element_id)
                    processed_elements.add(element_id)
                    break
        
        if elements_in_layer:  # Только непустые слои
            layer_elements[layer_coord] = elements_in_layer
    
    if on_progress:
        on_progress(73, f"Сортировка {len(layer_elements)} слоёв...")

    sorted_layers = dict(sorted(layer_elements.items(), key=lambda x: x[0]))
    
    print(f"Tolerance: {tolerance}")
    for i, layer in enumerate(sorted(sorted_layers.keys())):
        print(f"{i}: {layer:.6f}")
    
    return sorted_layers
