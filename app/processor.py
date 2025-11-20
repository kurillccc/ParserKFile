from typing import Dict, Tuple, List


def filter_elements_by_subregion(elements: Dict[int, Dict[str, List[int]]], target_subregion: int) -> Dict[
    int, List[int]]:
    """Фильтрует элементы, оставляя только те, что принадлежат заданной подобласти."""
    return {
        element_id: data["nodes"]
        for element_id, data in elements.items()
        if data["subregion"] == target_subregion
    }


def group_nodes_by_coordinate(nodes: Dict[int, Tuple[float, float, float]], coordinate: str) -> Dict[float, List[int]]:
    """Группирует узлы по координате X, Y или Z."""
    grouped_nodes: Dict[float, List[int]] = {}

    for node_id, (x, y, z) in nodes.items():
        if coordinate == "X":
            coord_value = x
        elif coordinate == "Y":
            coord_value = y
        elif coordinate == "Z":
            coord_value = z
        else:
            raise ValueError("Некорректная координата. Используйте 'X', 'Y' или 'Z'.")

        if coord_value not in grouped_nodes:
            grouped_nodes[coord_value] = []

        grouped_nodes[coord_value].append(node_id)

    return grouped_nodes


def find_h_and_home(nodes: Dict[int, Tuple[float, float, float]], coordinate: str) -> Tuple[
    float, Dict[int, Tuple[float, float, float]], List[Tuple[int, Tuple[float, float, float]]]]:
    """Находит высоту и координаты которые относятся к дому если он есть"""
    max_x = max_y = max_z = 0

    for x, y, z in nodes.values():
        if y == 0 and z == 0:
            max_x = max(max_x, x)
        if x == 0 and z == 0:
            max_y = max(max_y, y)
        if x == 0 and y == 0:
            max_z = max(max_z, z)

    # Определяем h, a, b
    if coordinate == 'X':
        h, a, b = max_x, max_y, max_z
    elif coordinate == 'Y':
        h, a, b = max_y, max_x, max_z
    elif coordinate == 'Z':
        h, a, b = max_z, max_x, max_y
    else:
        raise ValueError("Некорректная координата. Используйте 'X', 'Y' или 'Z'.")

    # Фильтруем узлы, оставляя только те, которые не превышают найденные a, b, h
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
    """Для каждого слоя находит элементы, связанные с узлами этого слоя."""
    grouped_nodes = group_nodes_by_coordinate(nodes, coordinate)

    layer_elements: Dict[float, List[int]] = {}
    processed_elements = set()  # Множество для отслеживания уже обработанных элементов

    rounded_layers = {}  # Словарь для хранения группированных слоёв
    tolerance: float = 1e-10

    for coord_value, node_ids in grouped_nodes.items():
        rounded_coord = round(coord_value / tolerance) * tolerance  # Округление с погрешностью

        if rounded_coord not in rounded_layers:
            rounded_layers[rounded_coord] = []
        rounded_layers[rounded_coord].extend(node_ids)

    for rounded_coord, node_ids in rounded_layers.items():
        elements_in_layer = []

        for element_id, node_ids_in_element in elements.items():
            if element_id not in processed_elements and any(node_id in node_ids for node_id in node_ids_in_element):
                elements_in_layer.append(element_id)
                processed_elements.add(element_id)

        layer_elements[rounded_coord] = elements_in_layer

    # Удаление последнего слоя, если он пустой
    if layer_elements and not layer_elements[list(layer_elements.keys())[-1]]:
        del layer_elements[list(layer_elements.keys())[-1]]

    # Сортируем чтобы потом все ок было
    layer_elements = dict(sorted(layer_elements.items(), key=lambda x: round(x[0], 6)))

    return layer_elements
