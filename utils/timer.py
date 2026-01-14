import time
from typing import Callable


class Timer:
    """Утилита для измерения времени"""

    def __init__(self):
        self.start_time = None
        self.elapsed_time: float = 0.0
        self.running: bool = False

    def start(self):
        """Запуск таймера"""
        self.start_time = time.perf_counter()
        self.running = True
        self.elapsed_time = 0.0

    def stop(self):
        """Остановка таймера"""
        if self.running and self.start_time:
            self.elapsed_time = time.perf_counter() - self.start_time
            self.running = False

    def get_elapsed_formatted(self) -> str:
        """Получение отформатированного времени"""
        if self.running and self.start_time:
            seconds = time.perf_counter() - self.start_time
        else:
            seconds = self.elapsed_time

        return Timer.format_time(seconds)

    @staticmethod
    def format_time(seconds: float) -> str:
        """Форматирование времени в читаемый вид"""
        if seconds < 1:
            return f"{int(seconds * 1000)} мс"

        minutes, sec = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        if days > 0:
            return f"{days} д {hours:02}:{minutes:02}:{sec:02}"
        if hours > 0:
            return f"{hours:02}:{minutes:02}:{sec:02}"
        if minutes > 0:
            return f"{minutes:02}:{sec:02}"

        return f"{sec} с"