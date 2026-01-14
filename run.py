import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict, Any

from app import (
    generate_layer_data,
    write_to_cd_by_k_word,
    parse_k_file,
    filter_elements_by_subregion,
    find_elements_for_layer,
    find_h_and_home,put_cell_sets,
    put_stress_set,
    put_set_solid
)
from ui import FileInput, TextInput, DropdownInput, ProgressDisplay, OutputText, ActionButton
from utils import ResultFormatter, InputValidator, Timer


class Application(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("ParserKFile")
        self.geometry("600x600")

        self.timer = Timer()
        self.timer_running = False

        self.input_k_file_path: str = ""
        self.input_cd_file_path: str = ""
        self.output_folder: str = "ParserKFile/app/data/output"

        self.resizable(False, False)

        self.create_widgets()

    def finish_processing_ui(self):
        self.timer_running = False
        self.timer.stop()
        self.process_button.config(state="normal")

    def run_process_data_with_cleanup(self):
        try:
            self.process_data()
        finally:
            self.after(0, self.finish_processing_ui)

    def run_in_thread(self):
        valid, error_msg = InputValidator.validate_file_paths(
            self.input_k_file_path,
            self.input_cd_file_path
        )
        if not valid:
            messagebox.showerror("Ошибка", error_msg)
            return

        self.progress_display.update_progress(0)
        self.progress_display.update_status("Подготовка...")

        self.output_text.clear()
        self.output_text.insert(ResultFormatter.format_processing_message())

        self.timer.start()
        self.timer_running = True
        self.update_timer()

        self.process_button.config(state="disabled")

        thread = threading.Thread(target=self.run_process_data_with_cleanup)
        thread.start()

    def create_widgets(self) -> None:
        """Создание элементов интерфейса"""

        self.k_file_input = FileInput(
            self,
            "Выбрать k файл",
            "Выберите файл k для обработки",
            self.select_input_k_file
        )
        self.k_file_input.grid(row=0, column=0, columnspan=2, sticky="we")

        self.cd_file_input = FileInput(
            self,
            "Выбрать cd файл",
            "Выберите файл cd для обработки",
            self.select_input_cd_file
        )
        self.cd_file_input.grid(row=1, column=0, columnspan=2, sticky="we")

        self.subregion_input = TextInput(self, "Введите номер подобласти:")
        self.subregion_input.grid(row=2, column=0, columnspan=2, sticky="we")

        self.density_input = TextInput(self, "Введите плотность:")
        self.density_input.grid(row=3, column=0, columnspan=2, sticky="we")

        self.pr_input = TextInput(self, "Введите коэффициент Пуассона PR:")
        self.pr_input.grid(row=4, column=0, columnspan=2, sticky="we")

        self.coordinate_input = DropdownInput(self, "Выберите координату (X, Y, Z):", ["X", "Y", "Z"])
        self.coordinate_input.grid(row=5, column=0, columnspan=2, sticky="we")

        self.process_button = ActionButton(self, "Обработать", self.run_in_thread)
        self.process_button.grid(row=6, column=0, columnspan=2, pady=7)

        self.progress_display = ProgressDisplay(self)
        self.progress_display.grid(row=7, column=0, columnspan=2, pady=0)

        self.output_text = OutputText(self)
        self.output_text.grid(row=8, column=0, columnspan=2, pady=5, sticky="nsew")

        self.grid_rowconfigure(8, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def update_progress(self, value: int, status: str):
        self.progress_display.update_progress(value)
        self.progress_display.update_status(status)

    def update_timer(self):
        if not self.timer_running:
            return

        elapsed = self.timer.get_elapsed_formatted()
        self.progress_display.update_time(f"Прошло: {elapsed}")

        self.after(10, self.update_timer)

    def select_input_k_file(self) -> None:
        """Открывает диалог для выбора файла"""
        self.input_k_file_path = filedialog.askopenfilename(title="Выберите k файл", filetypes=[("Text files", "*.k")])
        if self.input_k_file_path:
            self.k_file_input.update_label(os.path.basename(self.input_k_file_path))

    def select_input_cd_file(self) -> None:
        """Открывает диалог для выбора файла"""
        self.input_cd_file_path = filedialog.askopenfilename(title="Выберите cd файл",
                                                             filetypes=[("Text files", "*.cd")])
        if self.input_cd_file_path:
            self.cd_file_input.update_label(os.path.basename(self.input_cd_file_path))

    def process_data(self) -> None:
        """Обрабатывает данные при нажатии кнопки"""
        valid, error_msg = InputValidator.validate_file_paths(
            self.input_k_file_path,
            self.input_cd_file_path
        )
        if not valid:
            messagebox.showerror("Ошибка", error_msg)
            return

        valid, numbers, error_msg = InputValidator.validate_numbers(
            self.subregion_input.get(),
            self.density_input.get(),
            self.pr_input.get()
        )
        if not valid:
            messagebox.showerror("Ошибка", error_msg)
            return

        subregion, density, PR = numbers
        coordinate = self.coordinate_input.get()

        try:
            # === ЭТАП 1: Парсинг K-файла ===
            self.after(0, self.update_progress, 10, "Парсинг K-файла...")
            nodes, elements = parse_k_file(self.input_k_file_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при сборе данных по k файлу: {e}")
            return

        try:
            # === ЭТАП 2: Фильтрация элементов ===
            self.after(0, self.update_progress, 25, "Фильтрация элементов по подобласти...")
            filtered_elements = filter_elements_by_subregion(elements, subregion)

            # === ЭТАП 3: Поиск домика и высоты ===
            self.after(0, self.update_progress, 40, "Анализ геометрии модели...")
            h, nodes, nodes_outside = find_h_and_home(nodes, coordinate)

            # === ЭТАП 4: Формирование слоёв ===
            self.after(0, self.update_progress, 60, "Формирование слоёв расчетной сетки...")
            layer_elements = find_elements_for_layer(nodes, filtered_elements, coordinate)

            element_counts = [len(elements) for elements in layer_elements.values() if elements]

            if len(set(element_counts)) > 1:
                messagebox.showerror("Предупреждение", "Количество элементов в слоях не совпадает!")

            # === ЭТАП 5: Генерация напряжений ===
            self.after(0, self.update_progress, 75, "Формирование начальных напряжений...")
            data: Dict[str, Any] = generate_layer_data(len(layer_elements), coordinate, density, PR, h, layer_elements)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при обработке результатов: {e}")
            return

        try:
            # === ЭТАП 6: Запись файлов ===
            self.after(0, self.update_progress, 90, "Запись CD-файла...")
            output = write_to_cd_by_k_word(data, "CELL_SETS", self.input_cd_file_path, put_cell_sets)
            write_to_cd_by_k_word(data, "INITIAL_STRESS_SET", output, put_stress_set)
            output_path: str = write_to_cd_by_k_word(data, "SET_SOLID", output, put_set_solid)

            self.after(0, self.update_progress, 100, "Готово ✔")

            formatted_results = ResultFormatter.format_results(
                output_path=output_path,
                elements_count=len(elements),
                height=h,
                subregion=subregion,
                density=density,
                pr=PR,
                has_home=len(nodes_outside) != 0,
                coordinate=coordinate,
                elapsed_time=self.timer.get_elapsed_formatted(),
                cell_sets_marker=put_cell_sets,
                stress_set_marker=put_stress_set,
                solid_set_marker=put_set_solid
            )

            self.output_text.clear()
            self.output_text.insert(formatted_results)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при записи данных в cd файл: {e}")


if __name__ == "__main__":
    app = Application()
    app.mainloop()