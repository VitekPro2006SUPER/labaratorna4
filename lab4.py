import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QGroupBox, QMessageBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


def get_math_function(expression):
    allowed_names = {
        "x": 0, "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "exp": np.exp, "log": np.log, "sqrt": np.sqrt, "pi": np.pi,
        "abs": np.abs, "pow": np.power
    }
    
    def func(val):
        local_scope = allowed_names.copy()
        local_scope["x"] = val
        return eval(expression, {"__builtins__": {}}, local_scope)
    
    return func

def calc_lagrange(target_x, nodes_x, nodes_y):
    result = 0.0
    n = len(nodes_x)
    
    for i in range(n):
        # Базисний поліном
        basis = 1.0
        for j in range(n):
            if i != j:
                numerator = target_x - nodes_x[j]
                denominator = nodes_x[i] - nodes_x[j]
                basis *= numerator / denominator
        
        result += nodes_y[i] * basis
        
    return result

class InterpolationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторна: Метод Лагранжа")
        self.resize(900, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        control_panel = QVBoxLayout()
        
        # Група для меж інтервалу
        group_range = QGroupBox("Межі інтервалу [a, b]")
        range_layout = QVBoxLayout()
        
        self.input_a = QLineEdit("0")
        self.input_b = QLineEdit("6")
        
        range_layout.addWidget(QLabel("Початок (a):"))
        range_layout.addWidget(self.input_a)
        range_layout.addWidget(QLabel("Кінець (b):"))
        range_layout.addWidget(self.input_b)
        group_range.setLayout(range_layout)
        
        # Група для функції
        group_func = QGroupBox("Функція f(x)")
        func_layout = QVBoxLayout()
        self.input_expr = QLineEdit("sin(x) + 0.5*x")
        self.input_expr.setPlaceholderText("Наприклад: x**2 + cos(x)")
        
        func_layout.addWidget(QLabel("Вираз:"))
        func_layout.addWidget(self.input_expr)
        group_func.setLayout(func_layout)

        # Кнопка
        self.btn_calc = QPushButton("Обчислити та намалювати")
        self.btn_calc.setMinimumHeight(50)
        self.btn_calc.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.btn_calc.clicked.connect(self.plot_action)

        control_panel.addWidget(group_range)
        control_panel.addWidget(group_func)
        control_panel.addStretch()
        control_panel.addWidget(self.btn_calc)

        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        # Додавання в головний layout
        main_layout.addLayout(control_panel, stretch=1)
        main_layout.addWidget(self.canvas, stretch=3)

    def plot_action(self):
        try:
            # Зчитування даних
            a = float(self.input_a.text())
            b = float(self.input_b.text())
            expr_str = self.input_expr.text()

            if a >= b:
                raise ValueError("Початок інтервалу має бути меншим за кінець!")

            # Створення функції
            my_func = get_math_function(expr_str)

            # Генерація вузлів інтерполяції (10 відрізків -> 11 точок)
            count = 11
            nodes_x = np.linspace(a, b, count)
            nodes_y = my_func(nodes_x)

            # Точки для плавного графіка
            x_smooth = np.linspace(a, b, 400)
            y_original = my_func(x_smooth)
            
            # Обчислення полінома Лагранжа для кожної точки
            y_lagrange = [calc_lagrange(val, nodes_x, nodes_y) for val in x_smooth]

            # Візуалізація
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            # Графік оригіналу
            ax.plot(x_smooth, y_original, label="Вихідна функція f(x)", 
                    color="#1f77b4", linewidth=2)
            
            # Графік полінома
            ax.plot(x_smooth, y_lagrange, label="L(x) - Лагранж", 
                    color="#ff7f0e", linestyle="--", linewidth=2)
            
            # Вузлові точки
            ax.scatter(nodes_x, nodes_y, color="black", marker="x", s=50, zorder=5, label="Вузли")

            # Оформлення
            ax.set_title("Результат інтерполяції")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.legend()
            ax.grid(True, linestyle=':', alpha=0.6)

            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Сталася помилка при розрахунках:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InterpolationApp()
    window.show()
    sys.exit(app.exec())