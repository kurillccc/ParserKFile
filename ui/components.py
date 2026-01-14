import tkinter as tk
from tkinter import ttk, scrolledtext


class FileInput:
    """Компонент для выбора файла"""

    def __init__(self, parent, button_text, label_text, command):
        self.frame = tk.Frame(parent)

        self.frame.grid_columnconfigure(1, weight=1)

        self.button = tk.Button(self.frame, text=button_text, command=command)
        self.button.grid(row=0, column=0, pady=5, padx=(10, 5), sticky="w")

        spacer = tk.Frame(self.frame)
        spacer.grid(row=0, column=1, sticky="ew")

        self.label = tk.Label(self.frame, text=label_text, anchor="e")
        self.label.grid(row=0, column=2, pady=5, padx=(5, 10), sticky="e")

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def update_label(self, text):
        self.label.config(text=text)

    def get_widget(self):
        return self.frame

class TextInput:
    """Компонент для ввода параметров"""
    def __init__(self, parent, label_text):
        self.frame = tk.Frame(parent)

        self.frame.grid_columnconfigure(1, weight=1)

        self.label = tk.Label(self.frame, text=label_text, anchor="w")
        self.label.grid(row=0, column=0, pady=3, sticky="w", padx=10)

        self.entry = tk.Entry(self.frame)
        self.entry.grid(row=0, column=1, pady=3, sticky="e", padx=10)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def get(self):
        return self.entry.get()


class DropdownInput:
    """Компонент для выпадающего списка"""

    def __init__(self, parent, label_text, options):
        self.frame = tk.Frame(parent)

        self.frame.grid_columnconfigure(1, weight=1)

        self.label = tk.Label(self.frame, text=label_text, anchor="w")
        self.label.grid(row=0, column=0, pady=3, sticky="w", padx=10)

        self.variable = tk.StringVar(value=options[2] if options else "-")
        self.dropdown = tk.OptionMenu(self.frame, self.variable, *options)
        self.dropdown.grid(row=0, column=1, pady=3, sticky="e", padx=10)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def get(self):
        return self.variable.get()

    def get_widget(self):
        return self.frame


class ProgressDisplay:
    """Компонент для отображения прогресса"""

    def __init__(self, parent):
        self.frame = tk.Frame(parent)

        # Прогресс-бар
        self.progress = ttk.Progressbar(
            self.frame,
            orient="horizontal",
            length=550,
            mode="determinate",
            maximum=100
        )
        self.progress.grid(row=0, column=0, columnspan=2, pady=10)

        # Контейнер для статуса и времени
        self.status_frame = tk.Frame(self.frame)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="we", padx=10)

        # Статус выполнения
        self.status_label = tk.Label(self.status_frame, text="⌛Ожидание запуска", anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True)

        # Время
        self.time_label = tk.Label(self.status_frame, text="", anchor="e")
        self.time_label.pack(side="right")

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def update_progress(self, value):
        self.progress["value"] = value

    def update_status(self, text):
        self.status_label.config(text=text)

    def update_time(self, text):
        self.time_label.config(text=text)

    def get_widget(self):
        return self.frame


class OutputText:
    """Компонент для вывода текста"""

    def __init__(self, parent):
        self.text_widget = scrolledtext.ScrolledText(
            parent,
            height=20,
            width=84,
            wrap=tk.WORD,
            font=("Times New Roman", 13)
        )

    def grid(self, **kwargs):
        self.text_widget.grid(**kwargs)

    def clear(self):
        self.text_widget.delete(1.0, tk.END)

    def insert(self, content):
        self.text_widget.insert(tk.END, content)

    def get_widget(self):
        return self.text_widget


class ActionButton:
    """Компонент кнопки действия"""

    def __init__(self, parent, text, command):
        self.button = tk.Button(parent, text=text, command=command)

    def grid(self, **kwargs):
        self.button.grid(**kwargs)

    def config(self, **kwargs):
        self.button.config(**kwargs)

    def get_widget(self):
        return self.button