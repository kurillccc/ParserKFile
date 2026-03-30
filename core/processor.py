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
    tolerance: float = 0.76
    
    node_to_layer: Dict[int, float] = {}
    layer_nodes: Dict[float, List[int]] = {}
    
    sorted_nodes = sorted(nodes.items(), key=lambda item: item[1][coord_idx])
    
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
            node_to_layer[node_id] = coord_value
            layer_nodes[coord_value] = [node_id]
    
    element_layers: Dict[int, Set[float]] = {}
    
    for elem_id, elem_nodes in elements.items():
        layers = set()
        for node_id in elem_nodes:
            if node_id in node_to_layer:
                layers.add(node_to_layer[node_id])
        if layers:
            element_layers[elem_id] = layers
    
    layer_elements: Dict[float, List[int]] = {}
    for layer in sorted(layer_nodes.keys()):
        layer_elements[layer] = []
    
    for elem_id, layers in element_layers.items():
        for layer in layers:
            if layer in layer_elements:
                layer_elements[layer].append(elem_id)
    
    layer_elements = {layer: elements_list 
                     for layer, elements_list in layer_elements.items() 
                     if elements_list}
    
    print(f"Tolerance: {tolerance}")
    for i, layer in enumerate(sorted(layer_elements.keys())):
        print(f"{i}: {layer:.6f}")
    
    return layer_elements
