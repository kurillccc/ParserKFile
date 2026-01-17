import os
from typing import Dict, Any

import click

from app.generate_yaml import write_to_yaml, generate_layer_data, write_to_cd_by_k_word
from app.parser import parse_k_file
from app.processor import filter_elements_by_subregion, group_nodes_by_coordinate, find_elements_for_layer, \
    find_h_and_home
from app.settings import input_file_name, put_cell_sets, put_stress_set, put_set_solid
from settings import BASE_DIR


@click.command()
@click.option("--input-dir", default="data/input", help="Папка с исходными файлами")
@click.option("--subregion", default=1, type=int, help="Подобласть для фильтрации")
@click.option("--coordinate", default='Y', type=str, help="Координата для фильтрации слоев")
@click.option("--density", default=-1500.0, type=float, help="Плотность материала (кг/м³)")
@click.option("--pr", default=0.32, type=float, help="Коэффициент Пуассона PR")
@click.option("--output", default="data/output", help="Папка для сохранения")
def run(input_dir: str, subregion: int, coordinate: str, density: float, pr: float, output: str) -> None:
    input_dir = os.path.join(BASE_DIR, input_dir)
    k_file_path = os.path.join(input_dir, f"{input_file_name}.k")

    print("Чтение файла:", k_file_path)
    try:
        nodes, elements = parse_k_file(k_file_path)
    except Exception as e:
        print(f"Не удалось прочитать файл\nОшибка{e}")

    print(f"Фильтрация элементов по подобласти {subregion}...")
    try:
        filtered_elements = filter_elements_by_subregion(elements, subregion)

        print("Узлы:", nodes)
        print("Отфильтрованные элементы:", filtered_elements)
    except Exception as e:
        print(f"Не удалось отфильтровать элементы по подобласти\nОшибка{e}")

    print(f"Выделим наш прямоугольник от домика сверху и найдем высоту")
    try:
        h, nodes, nodes_outside = find_h_and_home(nodes, coordinate)
        print("Координаты нашего грунта")
        for node_id, (x, y, z) in nodes.items():
            print(f"Узел {node_id}: ({x}, {y}, {z})")
        print(f"Высота = {h}")
        print("Координаты нашего домика")
        if len(nodes_outside) != 0:
            for node_id, (x, y, z) in nodes_outside:
                print(f"Узел {node_id}: ({x}, {y}, {z})")
        else:
            print("А тут нет домика")

        print()
    except Exception as e:
        print(f"Не удалось отделить домик от прямоугольника\nОшибка {e}")

    print(f"Отберем id слов по порядку от 0 по координате {coordinate}\n")
    try:
        group_nodes = group_nodes_by_coordinate(nodes, coordinate)
        for coord_value, id in group_nodes.items():
            print(f"SID: {coordinate} = {coord_value}:")
            print(f"Count: {len(id)}")
            print("ID:")
            for element_id in id:
                print(f"      - {element_id}")
            print()
    except Exception as e:
        print(f"Не удалось отобрать id слоев\nОшибка {e}")

    print(f"Отбираем элементы, которые принадлежат слою по координате {coordinate}\n")
    try:
        layer_elements = find_elements_for_layer(nodes, filtered_elements, coordinate)
        for coord_value, elements_in_layer in layer_elements.items():
            print(f"SID: {coordinate} = {coord_value}:")
            print(f"Count: {len(elements_in_layer)}")
            print("ELEMENTS:")
            for element_id in elements_in_layer:
                print(f"      - {element_id}")
            print()
    except Exception as e:
        print(f"Не удалось отобрать элементы\nОшибка: {e}")

    print("Переведем файл в требуемый формат")
    try:
        data: Dict[str, Any] = generate_layer_data(len(layer_elements), coordinate, density, pr, h, layer_elements)

        write_to_yaml(data, input_dir, output)
        print(f"Файл сохранен в {output}")
    except Exception as e:
        print(f"Не удалось создать файл\nОшибка{e}")

    print("Вставим в cd файл чтобы получить готовый вариант")
    try:
        output = write_to_cd_by_k_word(data, "CELL_SETS", input_dir, put_cell_sets)
        write_to_cd_by_k_word(data, "INITIAL_STRESS_SET", output, put_stress_set)
        write_to_cd_by_k_word(data, "SET_SOLID", output, put_set_solid)

    except Exception as e:
        print(f"Не удалось сгенерировать файл\nОшибка{e}")

    print("Выполнено\n")


if __name__ == "__main__":
    run()
