import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict, Any

from app.generate_yaml import generate_layer_data, write_to_yaml, write_to_cd_by_k_word
from app.parser import parse_k_file
from app.processor import filter_elements_by_subregion, find_elements_for_layer, find_h_and_home
from app.settings import put_cell_sets, put_stress_set, put_set_solid


class Application(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Парсинг KFile")
        self.geometry("600x600")

        self.input_k_file_path: str = ""
        self.input_cd_file_path: str = ""
        self.output_folder: str = "ParserKFile/app/data/output"

        self.resizable(False, False)

        self.create_widgets()

    def finish_processing_ui(self):
        self.process_button.config(state="normal")

    def run_process_data_with_cleanup(self):
        try:
            self.process_data()
        finally:
            # Вернём управление в основной поток, чтобы включить кнопку
            self.after(0, self.finish_processing_ui)

    def run_in_thread(self):
        if not self.input_k_file_path:
            messagebox.showerror("Ошибка", "Выберите k файл для обработки")
            return
        if not self.input_cd_file_path:
            messagebox.showerror("Ошибка", "Выберите cd файл для обработки")
            return
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "⏳ Обработка... Пожалуйста, подождите.\n")

        self.process_button.config(state="disabled")

        # Запускаем поток
        thread = threading.Thread(target=self.run_process_data_with_cleanup)
        thread.start()

    def create_widgets(self) -> None:
        """Создание элементов интерфейса"""

        # Кнопка для выбора входного k файла
        self.input_k_button = tk.Button(self, text="Выбрать k файл", command=self.select_input_k_file)
        self.input_k_button.grid(row=0, column=0, pady=10, padx=10, sticky="w")

        # Поле для отображения выбранного k файла
        self.input_k_file_label = tk.Label(self, text="Выберите файл k для обработки")
        self.input_k_file_label.grid(row=0, column=1, pady=10, padx=10, sticky="w")

        # Кнопка для выбора входного cd файла
        self.input_cd_button = tk.Button(self, text="Выбрать cd файл", command=self.select_input_cd_file)
        self.input_cd_button.grid(row=1, column=0, pady=10, padx=10, sticky="w")

        # Поле для отображения выбранного cd файла
        self.input_cd_file_label = tk.Label(self, text="Выберите файл cd для обработки")
        self.input_cd_file_label.grid(row=1, column=1, pady=10, padx=10, sticky="w")

        # Ввод для подобласти
        self.subregion_label = tk.Label(self, text="Введите номер подобласти:")
        self.subregion_label.grid(row=2, column=0, pady=5, padx=10, sticky="w")

        # Текстовое поле для ввода номера подобласти
        self.subregion_entry = tk.Entry(self)
        self.subregion_entry.grid(row=2, column=1, pady=5, padx=10)

        # Ввод для плотности
        self.density_label = tk.Label(self, text="Введите плотность:")
        self.density_label.grid(row=3, column=0, pady=5, padx=10, sticky="w")

        # Текстовое поле для ввода плотности
        self.density_entry = tk.Entry(self)
        self.density_entry.grid(row=3, column=1, pady=5, padx=10)

        # Ввод для коэффициента Пуассона PR
        self.pr_label = tk.Label(self, text="Введите коэффициент Пуассона PR:")
        self.pr_label.grid(row=4, column=0, pady=5, padx=10, sticky="w")

        # Текстовое поле для ввода коэффициента Пуассона PR
        self.pr_entry = tk.Entry(self)
        self.pr_entry.grid(row=4, column=1, pady=5, padx=10)

        # Выпадающий список для выбора координаты (X, Y, Z)
        self.coordinate_label = tk.Label(self, text="Выберите координату (X, Y, Z):")
        self.coordinate_label.grid(row=5, column=0, pady=5, padx=10, sticky="w")

        self.coordinate_option = tk.OptionMenu(self, tk.StringVar(), *["X", "Y", "Z"])
        self.coordinate_option.grid(row=5, column=1, pady=5, padx=10)

        # Кнопка для обработки данных
        self.process_button = tk.Button(self, text="Обработать", command=self.run_in_thread)
        self.process_button.grid(row=6, column=0, columnspan=2, pady=20)

        # Текстовое поле для отображения результатов
        self.output_text = tk.Text(self, height=20, width=84)
        self.output_text.grid(row=7, column=0, columnspan=2, pady=10)

    def select_input_k_file(self) -> None:
        """Открывает диалог для выбора файла"""
        self.input_k_file_path = filedialog.askopenfilename(title="Выберите k файл", filetypes=[("Text files", "*.k")])
        if self.input_k_file_path:
            self.input_k_file_label.config(text=os.path.basename(self.input_k_file_path))

    def select_input_cd_file(self) -> None:
        """Открывает диалог для выбора файла"""
        self.input_cd_file_path = filedialog.askopenfilename(title="Выберите cd файл",
                                                             filetypes=[("Text files", "*.cd")])
        if self.input_cd_file_path:
            self.input_cd_file_label.config(text=os.path.basename(self.input_cd_file_path))

    def process_data(self) -> None:
        """Обрабатывает данные при нажатии кнопки"""
        if not self.input_k_file_path:
            messagebox.showerror("Ошибка", "Выберите k файл для обработки")
            return
        if not self.input_cd_file_path:
            messagebox.showerror("Ошибка", "Выберите cd файл для обработки")
            return
        try:
            subregion: int = int(self.subregion_entry.get())
            density: float = - float(self.density_entry.get())
            PR: float = float(self.pr_entry.get())
            coordinate: str = self.coordinate_option.cget("text")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка входных данных: {e}")
            return

        try:
            # Парсим файл
            nodes, elements = parse_k_file(self.input_k_file_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при сборе данных по k файлу: {e}")
            return

        try:
            # Фильтруем элементы
            filtered_elements = filter_elements_by_subregion(elements, subregion)

            # Отделяем домик и грунт
            h, nodes, nodes_outside = find_h_and_home(nodes, coordinate)

            # Находим элементы по слоям
            layer_elements = find_elements_for_layer(nodes, filtered_elements, coordinate)

            element_counts = [len(elements) for elements in layer_elements.values() if
                              elements]  # исключили пустые слои

            if len(set(element_counts)) > 1:
                messagebox.showerror("Предупреждение", "Количество элементов в слоях не совпадает!")

            data: Dict[str, Any] = generate_layer_data(len(layer_elements), coordinate, density, PR, h, layer_elements)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при обработке результатов: {e}")
            return

        try:
            output_file_path: str = write_to_yaml(data, self.input_k_file_path, self.output_folder)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при запаиси промежуточных результатов: {e}")

        try:
            # Сделай cd файл
            output = write_to_cd_by_k_word(data, "CELL_SETS", self.input_cd_file_path, put_cell_sets)
            write_to_cd_by_k_word(data, "INITIAL_STRESS_SET", output, put_stress_set)
            output_path: str = write_to_cd_by_k_word(data, "SET_SOLID", output, put_set_solid)

            # Отображаем результаты в текстовом поле
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Промежуточные и конечные результаты сохранены в {output_path}\n"
                                            f"\nВысота: {h}\n"
                                            f"{'Домик есть и его влияние учитывается' if len(nodes_outside) != 0 else 'Домика нет'}\n\n"
                                            f"CELL_SETS вставлен после {put_cell_sets}\n"
                                            f"INITIAL_STRESS_SET вставлен после {put_stress_set}\n"
                                            f"SET_SOLID вставлен после {put_set_solid}\n")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при записи данных в cd файл: {e}")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
