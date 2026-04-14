from typing import Dict, Any

from utils import InputValidator, generate_layer_data, write_to_cd_by_k_word
from .parser import parse_k_file, parse_yaml_file
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
            config.yaml_file,
        )
        if not valid:
            raise ValueError(error)
        
        # 2. Анализ yaml файла
        on_progress(5, "Анализ yaml файла...")
        k_file, cd_file = parse_yaml_file(config.yaml_file)

        # 3. Парсинг
        on_progress(10, "Парсинг K-файла...")
        nodes, elements = parse_k_file(k_file, on_progress=on_progress)

        # 4. Фильтрация
        on_progress(35, "Фильтрация элементов...")
        filtered = filter_elements_by_subregion(elements, config.subregion)

        # 5. Геометрия
        on_progress(40, "Анализ геометрии...")
        h, nodes, nodes_outside = find_h_and_home(nodes, config.coordinate)

        # 6. Слои
        on_progress(50, "Формирование слоёв...")
        layers = find_elements_for_layer(nodes, filtered, config.coordinate, config.heterogeneous_layer, on_progress=on_progress)

        # 7. Напряжения
        on_progress(75, "Формирование напряжений...")
        data: Dict[str, Any] = generate_layer_data(
            len(layers),
            config.coordinate,
            config.density,
            config.pr,
            h,
            layers
        )

        # 8. Запись
        on_progress(80, "Запись \"CELL_SETS\" в CD-файл...")
        output = write_to_cd_by_k_word(data, "CELL_SETS", cd_file, put_cell_sets)

        on_progress(87, "Запись \"INITIAL_STRESS_SET\" в CD-файл...")
        write_to_cd_by_k_word(data, "INITIAL_STRESS_SET", output, put_stress_set)

        on_progress(95, "Запись \"SET_SOLID\" в CD-файл...")
        output_path = write_to_cd_by_k_word(data, "SET_SOLID", output, put_set_solid)

        on_progress(100, "Готово ✔")

        return {
            "output_path": output_path,
            "elements_count": len(elements),
            "height": h,
            "has_home": len(nodes_outside) != 0
        }
