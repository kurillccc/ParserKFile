import os
from typing import Tuple, Optional


class InputValidator:
    """Валидация входных данных"""

    @staticmethod
    def validate_file_paths(k_path: str, cd_path: str) -> Tuple[bool, str]:
        """Проверка путей к файлам"""
        if not k_path:
            return False, "Выберите k файл для обработки"
        if not cd_path:
            return False, "Выберите cd файл для обработки"
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
            density_val = -float(density)  # Отрицательное значение
            pr_val = float(pr)
            return True, (subregion_val, density_val, pr_val), ""
        except ValueError as e:
            return False, None, f"Ошибка входных данных: {e}"

    @staticmethod
    def validate_file_exists(path: str) -> bool:
        """Проверка существования файла"""
        return os.path.exists(path) if path else False
