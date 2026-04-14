from typing import Dict, Any

from utils import InputValidator, generate_layer_data, write_to_cd_by_k_word
from .parser import parse_k_file
from .processor import (
    filter_elements_by_subregion,
    find_h_and_home,
    find_elements_for_layer
)
from .settings import (
    put_cell_sets,
    put_stress_set,
    put_set_solid
)


class ProcessingService:
    def process(self, config, on_progress):
        # 1. Валидация
        valid, error = InputValidator.validate_file_paths(
            config.k_file,
            config.cd_file
        )
        if not valid:
            raise ValueError(error)

        # 2. Парсинг
        on_progress(10, "Парсинг K-файла...")
        nodes, elements = parse_k_file(config.k_file)

        # 3. Фильтрация
        on_progress(25, "Фильтрация элементов...")
        filtered = filter_elements_by_subregion(elements, config.subregion)

        # 4. Геометрия
        on_progress(40, "Анализ геометрии...")
        h, nodes, nodes_outside = find_h_and_home(nodes, config.coordinate)

        # 5. Слои
        on_progress(60, "Формирование слоёв...")
        layers = find_elements_for_layer(nodes, filtered, config.coordinate, config.heterogeneous_layer)

        # 6. Напряжения
        on_progress(75, "Формирование напряжений...")
        data: Dict[str, Any] = generate_layer_data(
            len(layers),
            config.coordinate,
            config.density,
            config.pr,
            h,
            layers
        )

        # 7. Запись
        on_progress(90, "Запись CD-файла...")
        output = write_to_cd_by_k_word(data, "CELL_SETS", config.cd_file, put_cell_sets)
        write_to_cd_by_k_word(data, "INITIAL_STRESS_SET", output, put_stress_set)
        output_path = write_to_cd_by_k_word(data, "SET_SOLID", output, put_set_solid)

        on_progress(100, "Готово ✔")

        return {
            "output_path": output_path,
            "elements_count": len(elements),
            "height": h,
            "has_home": len(nodes_outside) != 0
        }
