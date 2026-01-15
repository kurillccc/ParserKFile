import platform


class ResultFormatter:
    """Форматирование результатов обработки"""

    @staticmethod
    def _get_separator() -> str:
        """Возвращает разделитель в зависимости от ОС"""
        system = platform.system()
        if system == "Windows":
            return "═" * 48
        elif system == "Darwin":
            return "=" * 62

    @staticmethod
    def format_results(
            output_path: str,
            elements_count: int,
            height: float,
            subregion: int,
            density: float,
            pr: float,
            has_home: bool,
            coordinate: str,
            elapsed_time: str,
            cell_sets_marker: str,
            stress_set_marker: str,
            solid_set_marker: str
    ) -> str:
        """Форматирует результаты в текст"""

        separator = ResultFormatter._get_separator()
        home_status = "Домик обнаружен (учитывается в расчетах)" if has_home else "Домик отсутствует"

        return f"""
{separator}
                                             РЕЗУЛЬТАТЫ ОБРАБОТКИ
{separator}

Файлы сохранены:
   {output_path}

Статистика модели:
   • Конечных элементов: {elements_count:,} шт
   • Высота модели: {height:.2f} единиц
   • Подобласть: {subregion}
   • Плотность: {abs(density):.3f}
   • Коэффициент Пуассона: {pr:.3f}

Особенности геометрии:
   • {home_status}
   • Координата анализа: {coordinate}

Производительность:
   • Время обработки: {elapsed_time}

Сгенерированные блоки:
   • CELL_SETS → после '{cell_sets_marker}'
   • INITIAL_STRESS_SET → после '{stress_set_marker}'
   • SET_SOLID → после '{solid_set_marker}'
"""

    @staticmethod
    def format_processing_message() -> str:
        """Сообщение во время обработки"""
        return "⏳ Обработка... Пожалуйста, подождите.\n"

    @staticmethod
    def format_error_message(error: str) -> str:
        """Форматирование сообщения об ошибке"""
        return f"❌ Ошибка: {error}"
