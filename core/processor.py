from typing import Dict, Tuple, List


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

    grouped_nodes = group_nodes_by_coordinate(nodes, coordinate)

    layer_elements: Dict[float, List[int]] = {}
    processed_elements = set()

    tolerance: float = 1e-10
    rounded_layers: Dict[float, List[int]] = {}

    # --- группируем слои ---
    for coord_value, node_ids in grouped_nodes.items():
        rounded_coord = round(coord_value / tolerance) * tolerance
        rounded_layers.setdefault(rounded_coord, []).extend(node_ids)

    elements_items = list(elements.items())  # локальная ссылка

    # --- основной цикл ---
    for rounded_coord, node_ids in rounded_layers.items():
        node_ids_set = set(node_ids)  # КЛЮЧЕВОЕ УСКОРЕНИЕ
        elements_in_layer = []

        for element_id, element_nodes in elements_items:
            if element_id in processed_elements:
                continue

            # fast check
            for nid in element_nodes:
                if nid in node_ids_set:
                    elements_in_layer.append(element_id)
                    processed_elements.add(element_id)
                    break

        layer_elements[rounded_coord] = elements_in_layer

    # удаляем последний пустой слой
    if layer_elements:
        last_key = next(reversed(layer_elements))
        if not layer_elements[last_key]:
            del layer_elements[last_key]

    return dict(sorted(layer_elements.items(), key=lambda x: round(x[0], 6)))
