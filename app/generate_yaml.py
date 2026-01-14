import os
import sys
import yaml
import uuid
import tempfile

from typing import Dict, List, Any
from app.settings import input_file_name, output_file_name, BASE_DIR


class CustomDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(CustomDumper, self).increase_indent(flow, False)


def generate_unique_id() -> str:
    """Генерация уникального идентификатора."""
    return uuid.uuid4().hex


def generate_layer_data(
        num_layers: int,
        coordinate: str,
        density: float,
        PR: float,
        h: float,
        layer_elements: Dict[float, List[int]]
) -> Dict[str, Any]:
    cell_sets = []
    initial_stress_set = []
    set_solid = []

    g = 9.8
    h_div = h / num_layers
    layers_count = len(layer_elements)

    # --- заранее выбираем ось ---
    if coordinate == 'X':
        stress_idx = 0
    elif coordinate == 'Y':
        stress_idx = 1
    elif coordinate == 'Z':
        stress_idx = 2
    else:
        raise ValueError("Некорректная координата")

    for i, (coord_value, elements_in_layer) in enumerate(layer_elements.items(), start=1):
        unic_id = uuid.uuid4().hex
        new_unic_id = uuid.uuid4().hex

        h_for_layer = h_div * (layers_count - i) + h_div * 0.5

        sig_main = density * g * h_for_layer
        sig = sig_main * PR / (1 - PR)

        sigs = [sig, sig, sig]
        sigs[stress_idx] = sig_main
        sigxx, sigyy, sigzz = sigs

        cell_sets.append({
            'Id': i,
            'Name': f'set{i}',
            'Count': len(elements_in_layer),
            '_ref_used_': 1,
            'uid': unic_id,
            'parentUid': '',
            '__excludeRun__': '~'
        })

        initial_stress_set.append({
            'ESID': i,
            'SIGXX': sigxx,
            'SIGYY': sigyy,
            'SIGZZ': sigzz,
            'SIGXY': 0,
            'SIGYZ': 0,
            'SIGZX': 0,
            'EPS': 0,
            'name': f'set{i}',
            'uid': new_unic_id,
            'parentUid': '',
            '__excludeRun__': '~'
        })

        set_solid.append({
            'NAME': f'set{i}',
            'SID': i,
            'ELEMENTS': elements_in_layer
        })

    return {
        'CELL_SETS': cell_sets,
        'INITIAL_STRESS_SET': initial_stress_set,
        'SET_SOLID': set_solid
    }


def get_output_dir():
    if getattr(sys, 'frozen', False):
        # Если приложение собрано в .exe или .app — сохраняем на рабочий стол
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop", "output")
        os.makedirs(desktop_dir, exist_ok=True)
        return desktop_dir
    else:
        # В режиме разработки сохраняем в проект
        output_dir = os.path.join(BASE_DIR, "data", "output")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir


def write_to_yaml(data: Dict[str, Any], file_path: str, output_path: str) -> str:
    """Запись данных в YAML файл."""
    # Получаем директорию, откуда брать имя файла
    directory: str = os.path.dirname(file_path)

    # Имя для файла
    output_name = f"{output_file_name}_debug.txt"

    output_dir = get_output_dir()

    # Создаём директорию, если её нет
    os.makedirs(output_dir, exist_ok=True)

    # Финальный путь к файлу
    output_file_path: str = os.path.join(output_dir, output_name)

    # Запись в YAML
    with open(output_file_path, 'w', encoding="utf-8") as file:
        yaml.dump(data, file, Dumper=CustomDumper, default_flow_style=False, allow_unicode=True, sort_keys=False,
                  indent=2)

    return directory


def write_to_cd_by_k_word(
        data: Dict[str, Any],
        section_name: str,
        file_path_cd: str,
        key_words: List[str]
) -> str:
    # --- нормализуем путь ---
    if not file_path_cd.endswith(".cd"):
        if "output" not in file_path_cd:
            file_path_cd = os.path.join(file_path_cd, f"{input_file_name}.cd")
        else:
            file_path_cd = os.path.join(BASE_DIR, "data", "output", f"{output_file_name}.cd")

    insert_block = yaml.dump(
        {section_name: data[section_name]},
        Dumper=CustomDumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        indent=2
    )

    found_key_word = False
    inserting_done = False

    # --- временный файл рядом ---
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".cd", dir=os.path.dirname(file_path_cd))
    os.close(tmp_fd)

    try:
        with open(file_path_cd, "r", encoding="utf-8", errors="ignore") as src, \
                open(tmp_path, "w", encoding="utf-8") as dst:

            for line in src:
                stripped = line.strip()

                if found_key_word and not inserting_done:
                    if not line.startswith((" ", "\t")):
                        dst.write(insert_block)
                        inserting_done = True

                if stripped in key_words:
                    found_key_word = True

                dst.write(line)

            # если ключ был, но вставки так и не случилось (ключ в конце файла)
            if found_key_word and not inserting_done:
                dst.write("\n")
                dst.write(insert_block)

        # атомарная замена
        os.replace(tmp_path, file_path_cd)

    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise RuntimeError(f"Не удалось вставить данные в cd файл: {e}")

    # --- путь вывода ---
    if getattr(sys, 'frozen', False):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "output")
        os.makedirs(desktop_path, exist_ok=True)
        output_file_path = os.path.join(desktop_path, os.path.basename(file_path_cd))
    else:
        output_dir = os.path.join(BASE_DIR, "data", "output")
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, os.path.basename(file_path_cd))

    # если надо копировать результат отдельно
    if output_file_path != file_path_cd:
        with open(file_path_cd, "r", encoding="utf-8") as src, \
                open(output_file_path, "w", encoding="utf-8") as dst:
            dst.writelines(src)

    return output_file_path
