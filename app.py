import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

class PatternApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego de Patrones - Versión Final")
        self.root.geometry("1000x700")
        self.root.configure(bg='#e3f2fd')
        
        # Configurar cierre apropiado
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Inicializar variables y UI
        self.initialize_variables()
        self.setup_styles()
        self.create_ui()
        
        # Cache de figuras y figura actual
        self.figure_cache = {}
        self.current_figure = None
        
        # Comenzar el juego después de la inicialización
        self.root.after(100, self.show_pattern)
        self.update_control_frame()

    def initialize_variables(self):
        self.score = 0
        self.level = 1
        self.attempts = 3
        self.completed_patterns = set()
        self.current_pattern = []
        self.correct_answer = ''
        self.patterns = self.create_patterns()

    def create_patterns(self):
        return {
            1: [(['○', '△', '○', '△'], '○'),
                (['□', '○', '□', '○'], '□'),
                (['△', '□', '△', '□'], '△')],
            2: [(['○', '△', '□', '○', '△'], '□'),
                (['△', '○', '△', '□', '○'], '△'),
                (['□', '○', '□', '△', '○'], '□')],
            3: [(['○', '△', '□', '○', '△', '□'], '○'),
                (['△', '□', '○', '△', '□', '○'], '△'),
                (['□', '○', '△', '□', '○', '△'], '□')],
            4: [
                (['2', '4', '8', '16', '32'], '64'),  # Duplicar el número (x2)
                (['1', '4', '9', '16', '25'], '36'),  # Cuadrados perfectos (n^2)
                (['5', '10', '15', '20', '25'], '30'),  # Incremento de 5 (n+5)
                (['3', '9', '27', '81', '243'], '729'),  # Potencias de 3 (n*3)
                (['2', '3', '5', '8', '13'], '21'),  # Secuencia de Fibonacci
                (['7', '14', '28', '56', '112'], '224'),  # Multiplicación por 2 (n*2)
                (['10', '20', '30', '40', '50'], '60'),  # Incremento constante de 10
                (['1', '2', '6', '24', '120'], '720')  # Factoriales (n!)
            ]
        }

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#e3f2fd')
        style.configure('TLabel', background='#e3f2fd', font=('Helvetica', 12), foreground="#37474f")
        style.configure('TButton', font=('Helvetica', 11), background="#ffcc80", foreground="#37474f", padding=5)
        style.map('TButton', background=[('active', '#ffab40')])

    def create_ui(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill="both")

        # Título
        ttk.Label(self.main_frame, text="Juego de Patrones", 
        font=('Helvetica', 28, 'bold'), foreground='#ff6f00').pack(pady=10)

        # Frame de información
        self.create_info_frame()

        # Canvas para la figura
        self.create_canvas_frame()

        # Botones de respuesta
        self.create_control_frame()

        # Elementos adicionales
        self.create_additional_elements()

    def create_info_frame(self):
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill="x", pady=10)

        self.info_labels = {}
        label_texts = ['Nivel', 'Puntaje', 'Intentos']
        
        for text in label_texts:
            self.info_labels[text.lower()] = ttk.Label(info_frame, font=('Helvetica', 14, 'bold'))
            self.info_labels[text.lower()].pack(side="left", padx=20)
        
        self.update_labels()

    def create_canvas_frame(self):
        canvas_frame = ttk.Frame(self.main_frame)
        canvas_frame.pack(pady=20)
        self.canvas = tk.Canvas(canvas_frame, width=800, height=300, 
            bg='#ffffff', bd=0, highlightthickness=0)
        self.canvas.pack()

    def create_control_frame(self):
            self.control_frame = ttk.Frame(self.main_frame)
            self.control_frame.pack(pady=20)

            # Campo de entrada para nivel 4
            self.entry_var = tk.StringVar()
            self.number_entry = ttk.Entry(self.control_frame, textvariable=self.entry_var)
            self.number_entry.bind('<Return>', lambda event: self.check_answer(self.entry_var.get()))
            self.submit_button = ttk.Button(self.control_frame, text="Enviar", 
                        command=lambda: self.check_answer(self.entry_var.get()))

            # Botones de figuras para niveles 1-3
            self.symbol_buttons = []
            possible_answers = ['○', '△', '□']
            for i, symbol in enumerate(possible_answers):
                button = ttk.Button(self.control_frame, text=symbol, width=5,
                            command=lambda s=symbol: self.check_answer(s))
                self.symbol_buttons.append(button)

            self.update_control_frame()

    """ MAKE IT WITH IA :D """
    def update_control_frame(self):
        # Limpiar frame
        for widget in self.control_frame.winfo_children():
            widget.grid_remove()

        if self.level == 4:
            self.number_entry.grid(row=0, column=0, padx=5, pady=5)
            self.submit_button.grid(row=0, column=1, padx=5, pady=5)
        else:
            for i, button in enumerate(self.symbol_buttons):
                row, col = divmod(i, 4)
                button.grid(row=row, column=col, padx=5, pady=5)

    def create_additional_elements(self):
        self.result_label = ttk.Label(self.main_frame, text="", font=('Helvetica', 14, 'bold'))
        self.result_label.pack(pady=10)

        ttk.Button(self.main_frame, text="Nuevo Patrón", 
                command=self.show_pattern).pack(pady=10)

        ttk.Label(self.main_frame, 
        text="¡Encuentra la siguiente figura en el patrón! Completa todos los patrones para avanzar.", 
        font=('Helvetica', 12), foreground="#455a64").pack(pady=10)

    def show_pattern(self):
        available_patterns = [(i, pattern) for i, pattern in enumerate(self.patterns[self.level]) 
            if i not in self.completed_patterns]
        
        if not available_patterns:
            if self.level < 4:
                self.level_up()
            else:
                self.game_completed()
            return

        pattern_index, pattern_tuple = random.choice(available_patterns)
        self.current_pattern_index = pattern_index
        self.current_pattern = pattern_tuple[0] + ['?']
        self.correct_answer = pattern_tuple[1]

        # Usar cache para la figura
        cache_key = str(self.current_pattern)
        if cache_key in self.figure_cache:
            self.show_cached_figure(cache_key)
        else:
            self.create_and_cache_figure(cache_key)

    """ MORE IA """
    def create_and_cache_figure(self, cache_key):
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.axis('off')
        for i, shape in enumerate(self.current_pattern):
            ax.text(0.1 + i * 0.15, 0.5, shape, fontsize=40, ha='center')
        plt.tight_layout()
        
        self.figure_cache[cache_key] = fig
        self.show_cached_figure(cache_key)
    """ IA AGAIN """
    def show_cached_figure(self, cache_key):
        if self.current_figure:
            self.current_figure.get_tk_widget().destroy()
        
        fig = self.figure_cache[cache_key]
        self.current_figure = FigureCanvasTkAgg(fig, self.canvas)
        self.current_figure.draw()
        self.current_figure.get_tk_widget().pack()

    def check_answer(self, user_answer):
        if self.level == 4:
            try:
                user_answer = int(user_answer)
                is_correct = str(user_answer) == self.correct_answer
            except ValueError:
                self.result_label.config(
                    text="Por favor, ingresa solo números",
                    foreground="red"
                )
                return
        else:
            is_correct = user_answer == self.correct_answer

        if is_correct:
            self.handle_correct_answer()
        else:
            self.handle_incorrect_answer()

        self.update_labels()
        if self.attempts > 0:
            self.entry_var.set("")
            self.root.after(100, self.show_pattern)


    def handle_correct_answer(self):
        self.score += self.level * 10
        self.completed_patterns.add(self.current_pattern_index)
        self.result_label.config(
            text=f"¡Correcto! +{self.level * 10} puntos", 
            foreground="green"
        )

        if len(self.completed_patterns) == len(self.patterns[self.level]):
            if self.level < 4:
                self.level_up()
            else:
                self.game_completed()

    def handle_incorrect_answer(self):
        self.attempts -= 1
        self.result_label.config(
            text=f"Incorrecto. La respuesta era {self.correct_answer}. "
            f"Te quedan {self.attempts} intentos", 
            foreground="red"
        )
        
        if self.attempts <= 0:
            self.game_over()

    def level_up(self):
        self.level += 1
        self.completed_patterns.clear()
        self.update_control_frame()
        messagebox.showinfo("¡Felicitaciones!", 
            f"¡Nivel {self.level-1} completado! "
            f"Avanzas al nivel {self.level}.")


    def game_completed(self):
        messagebox.showinfo("¡Felicitaciones!", 
            f"¡Has completado todos los niveles!\n"
            f"Puntaje final: {self.score}")
        self.reset_game()

    def game_over(self):
        messagebox.showinfo("Fin del juego", 
        f"¡Juego terminado!\nPuntaje final: {self.score}")
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.level = 1
        self.attempts = 3
        self.completed_patterns.clear()
        self.figure_cache.clear()
        self.update_control_frame()
        self.update_labels()


    def update_labels(self):
        texts = {
            'nivel': f"Nivel: {self.level}",
            'puntaje': f"Puntaje: {self.score}",
            'intentos': f"Intentos: {self.attempts}"
        }
        for key, text in texts.items():
            self.info_labels[key].config(text=text)



    def on_closing(self):
        # Limpiar recursos antes de cerrar
        plt.close('all')
        for fig in self.figure_cache.values():
            plt.close(fig)
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PatternApp(root)
    root.mainloop()