from typing import Dict, Tuple, List, Set


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
    coordinate: str
) -> Dict[float, List[int]]:
    coord_idx = {'x': 0, 'y': 1, 'z': 2}[coordinate.lower()]
    tolerance: float = 1e-2
    
    node_to_layer: Dict[int, float] = {}
    layer_nodes: Dict[float, List[int]] = {}
    
    sorted_nodes = sorted(nodes.items(), key=lambda item: item[1][coord_idx])
    
    for node_id, (x, y, z) in sorted_nodes:
        coord_value = (x, y, z)[coord_idx]
        rounded_coord = round(coord_value / tolerance) * tolerance
        node_to_layer[node_id] = rounded_coord
        
        if rounded_coord not in layer_nodes:
            layer_nodes[rounded_coord] = []
        layer_nodes[rounded_coord].append(node_id)

    element_layers: Dict[int, Set[float]] = {}
    
    for elem_id, elem_nodes in elements.items():
        layers = set()
        for node_id in elem_nodes:
            if node_id in node_to_layer:
                layers.add(node_to_layer[node_id])
        if layers:
            element_layers[elem_id] = layers
    
    layer_elements: Dict[float, List[int]] = {}
    for layer in layer_nodes.keys():
        layer_elements[layer] = []
    
    for elem_id, layers in element_layers.items():
        for layer in layers:
            if layer in layer_elements:
                layer_elements[layer].append(elem_id)
    
    if layer_elements:
        last_layer = next(reversed(list(layer_elements.keys())))
        if not layer_elements[last_layer]:
            del layer_elements[last_layer]
    
    return layer_elements