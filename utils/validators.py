import os
from typing import Tuple, Optional


class InputValidator:
    """Валидация входных данных"""

    @staticmethod
    def validate_file_paths(yaml_path: str) -> Tuple[bool, str]:
        """Проверка путей к файлам"""
        if not yaml_path:
            return False, "Выберите yaml файл для обработки"
        return True, ""

    @staticmethod
    def validate_numbers(
            subregion: str,
            density: str,
            pr: str
    ) -> Tuple[bool, Optional[Tuple[int, float, float]], str]:
        """Проверка числовых параметров"""
        try:
            subregion_val = int(subregion)
            density_val = -float(density)
            pr_val = float(pr)
            return True, (subregion_val, density_val, pr_val), ""
        except ValueError as e:
            return False, None, f"Ошибка входных данных: {e}"

    @staticmethod
    def validate_file_exists(path: str) -> bool:
        """Проверка существования файла"""
        return os.path.exists(path) if path else False
