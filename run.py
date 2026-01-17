import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from core import ProcessingConfig, ProcessingService
from ui import FileInput, TextInput, DropdownInput, ProgressDisplay, OutputText, ActionButton
from utils import ResultFormatter, InputValidator, Timer


class Application(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.service = ProcessingService()

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
        self.progress_display.update_progress(0)
        self.progress_display.update_status("Подготовка...")

        self.output_text.clear()
        self.output_text.insert(ResultFormatter.format_processing_message())

        self.timer.start()
        self.timer_running = True
        self.update_timer()

        self.process_button.config(state="disabled")

        threading.Thread(
            target=self.run_process_data_with_cleanup,
            daemon=True
        ).start()

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
        try:
            valid, numbers, error_msg = InputValidator.validate_numbers(
                self.subregion_input.get(),
                self.density_input.get(),
                self.pr_input.get()
            )
            if not valid:
                raise ValueError(error_msg)

            subregion, density, pr = numbers

            config = ProcessingConfig(
                k_file=self.input_k_file_path,
                cd_file=self.input_cd_file_path,
                subregion=subregion,
                density=density,
                pr=pr,
                coordinate=self.coordinate_input.get()
            )

            result = self.service.process(
                config,
                on_progress=lambda v, s: self.after(
                    0, self.update_progress, v, s
                )
            )

            formatted = ResultFormatter.format_results(
                output_path=result["output_path"],
                elements_count=result["elements_count"],
                height=result["height"],
                subregion=subregion,
                density=density,
                pr=pr,
                has_home=result["has_home"],
                coordinate=config.coordinate,
                elapsed_time=self.timer.get_elapsed_formatted()
            )

            self.output_text.clear()
            self.output_text.insert(formatted)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    app = Application()
    app.mainloop()
