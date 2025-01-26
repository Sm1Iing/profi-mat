import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sympy as sp
from sympy import log as symlog, sympify


class GraphingCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Графический калькулятор для логарифмических функций")
        self.root.geometry("1000x800")

        # Список для хранения графиков
        self.plots = []
        self.colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']  # Цвета для графиков

        # Создаем фигуру и оси
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
        self.ax.axvline(0, color='black', linewidth=0.5, linestyle='--')

        # Создаем canvas для отображения графика
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Поле для ввода функции
        self.function_label = ttk.Label(self.root, text="Введите функцию (используйте 'x' как переменную):")
        self.function_label.pack(pady=5)

        self.function_entry = ttk.Entry(self.root, width=50)
        self.function_entry.pack(pady=5)

        # Кнопка для добавления графика
        self.add_button = ttk.Button(self.root, text="Добавить график", command=self.add_plot)
        self.add_button.pack(pady=5)

        # Кнопка для очистки графика
        self.clear_button = ttk.Button(self.root, text="Очистить график", command=self.clear_plot)
        self.clear_button.pack(pady=5)

        # Подключение событий мыши
        self.canvas.mpl_connect("scroll_event", self.on_scroll)  # Приближение/отдаление
        self.canvas.mpl_connect("button_press_event", self.on_press)  # Нажатие кнопки мыши
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)  # Перемещение мыши
        self.canvas.mpl_connect("button_release_event", self.on_release)  # Отпускание кнопки мыши

        # Переменные для перемещения графика
        self.press = None
        self.original_xlim = None
        self.original_ylim = None

    def add_plot(self):
        """Добавляет график функции на рисунок."""
        expression = self.function_entry.get()
        if not expression:
            return

        try:
            #преобразуем введенную строку в символьное выражение
            x = sp.symbols('x')

            #заменяем log(x, base) на log(x)/log(base)
            expression = expression.replace("log(", "sp.log(")  # Заменяем log на sp.log
            expr = eval(expression, {"sp": sp, "x": x})  # Вычисляем выражение

            #определяем область определения функции
            if any(func.__name__ == 'log' for func in expr.atoms(sp.Function)):
                print("Функция содержит логарифм (log(x, base)), который определен только для x > 0.")
                x_min = 0.1
                x_max = 10
            else:
                x_min = -10
                x_max = 10

            #преобразуем символьное выражение в функцию, которую можно вычислить
            func = sp.lambdify(x, expr, 'numpy')

            #x
            x_vals = np.linspace(x_min, x_max, 1000)

            #y
            y_vals = func(x_vals)

            color = self.colors[len(self.plots) % len(self.colors)]  # Выбираем цвет
            self.ax.plot(x_vals, y_vals, label=f'y = {expression}', color=color, linewidth=2)
            self.plots.append((x_vals, y_vals, expression, color))

            self.ax.legend(loc='upper right', fontsize=10)
            self.canvas.draw()

        except Exception as e:
            print(f"Ошибка: {e}. Пожалуйста, убедитесь, что вы ввели корректное математическое выражение.")

    def clear_plot(self):
        self.ax.clear()
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
        self.ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
        self.plots.clear()
        self.canvas.draw()

    def on_scroll(self, event):
        scale_factor = 1.1 if event.button == 'up' else 0.9
        self.ax.set_xlim(self.ax.get_xlim()[0] * scale_factor, self.ax.get_xlim()[1] * scale_factor)
        self.ax.set_ylim(self.ax.get_ylim()[0] * scale_factor, self.ax.get_ylim()[1] * scale_factor)
        self.canvas.draw()

    def on_press(self, event):
        if event.button == 1:  # Левая кнопка мыши
            self.press = (event.xdata, event.ydata)
            self.original_xlim = self.ax.get_xlim()
            self.original_ylim = self.ax.get_ylim()

    def on_motion(self, event):
        if self.press is None or event.xdata is None or event.ydata is None:
            return

        dx = event.xdata - self.press[0]
        dy = event.ydata - self.press[1]

        self.ax.set_xlim(self.original_xlim[0] - dx, self.original_xlim[1] - dx)
        self.ax.set_ylim(self.original_ylim[0] - dy, self.original_ylim[1] - dy)
        self.canvas.draw()

    def on_release(self, event):
        self.press = None


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphingCalculator(root)
    root.mainloop()