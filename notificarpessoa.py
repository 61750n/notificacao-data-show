import tkinter as tk
from screeninfo import get_monitors
import threading
import time

class ScrollingTextApp:
    def __init__(self, master):
        # Configuração da janela principal
        self.master = master
        self.master.title("Botões")
        self.master.geometry(f"{self.master.winfo_screenwidth()}x200+0+0")  # Aumentei a altura para acomodar o controle deslizante

        # Botões e controles na janela principal
        self.write_button = tk.Button(master, text="Escrever", command=self.write_text)
        self.write_button.pack(side=tk.LEFT, padx=5)
        self.display_button = tk.Button(master, text="Exibir", command=self.display_text)
        self.display_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(master, text="Parar", command=self.stop_text)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.new_button = tk.Button(master, text="Novo", command=self.new_text)
        self.new_button.pack(side=tk.LEFT, padx=5)
        self.exit_button = tk.Button(master, text="Sair", command=self.master.destroy)
        self.exit_button.pack(side=tk.LEFT, padx=5)

        # Controle deslizante para ajustar a velocidade do scrolling
        self.speed_label = tk.Label(master, text="Velocidade do Scrolling:")
        self.speed_label.pack(pady=5)
        self.scroll_speed = tk.DoubleVar()
        self.scroll_speed.set(1.0)  # Valor padrão
        self.speed_slider = tk.Scale(master, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.scroll_speed, length=200)
        self.speed_slider.pack(pady=5)

        # Lista para armazenar frases anteriores
        self.previous_texts = []
        self.display_window = None
        self.is_scrolling = False

        # Entrada para digitar a frase
        self.entry_label = tk.Label(master, text="Digite a frase:")
        self.entry_label.pack(pady=5)
        self.entry = tk.Entry(master, width=40)
        self.entry.pack(pady=5)

    def write_text(self):
        # Função para escrever a frase e adicionar à lista
        current_text = self.entry.get()
        if current_text:
            self.app.previous_texts.append(current_text)
            if len(self.app.previous_texts) > 5:
                self.app.previous_texts.pop(0)
            self.entry.delete(0, tk.END)

    def display_text(self):
        # Função para exibir a frase na segunda janela
        if not self.is_scrolling:
            self.is_scrolling = True
            text_to_display = self.entry.get()
            if text_to_display:
                self.display_window = DisplayWindow(self.master, self, text_to_display)
                self.display_window.show()

    def stop_text(self):
        # Função para parar o scrolling
        if self.is_scrolling:
            self.is_scrolling = False
            if self.display_window:
                self.display_window.destroy()
                self.display_window = None

    def new_text(self):
        # Função para limpar a entrada ao clicar em Novo
        self.stop_text()
        if self.display_window:
            self.display_window.text_to_scroll.set("")
            self.display_window.displayed_text.set("")
        self.entry.delete(0, tk.END)


class DisplayWindow(tk.Toplevel):
    def __init__(self, master, app, text_to_display):
        # Configuração da segunda janela
        super().__init__(master)
        self.app = app
        self.title("Área de Exibição")

        # Configuração da posição da segunda janela no segundo monitor
        monitors = get_monitors()
        if len(monitors) > 1:
            second_monitor = monitors[1]
            self.geometry(f"{second_monitor.width}x50+{second_monitor.width}+{second_monitor.y}")

        # Configurações para remover a barra de título e botões de controle
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Frame para envolver o conteúdo na segunda janela
        frame = tk.Frame(self, bg="#FFD700")
        frame.pack(fill=tk.BOTH, expand=True)

        # Variáveis para texto a ser exibido e texto atualmente exibido
        self.text_to_scroll = tk.StringVar(value=text_to_display)
        self.displayed_text = tk.StringVar()
        self.scroll_display = tk.Label(frame, textvariable=self.displayed_text, font=("Arial", 16), height=5, bg="#FFD700")
        self.scroll_display.pack(fill=tk.X, expand=True)

        # Inicialização da thread de scrolling
        self.scroll_thread = None

    def show(self):
        # Função para exibir a segunda janela
        self.update_display()
        self.scroll_text()

    def update_display(self):
        # Atualiza o texto exibido na segunda janela
        new_text = self.text_to_scroll.get()
        self.displayed_text.set(new_text)
        self.scroll_display.configure(width=self.winfo_width())

    def scroll_text(self):
        # Inicia a thread de scrolling
        if self.app.is_scrolling:
            self.scroll_thread = threading.Thread(target=self.scroll_text_thread)
            self.scroll_thread.start()

    def scroll_text_thread(self):
        # Função que realiza o scrolling
        original_text = self.displayed_text.get()
        text_length = len(original_text)

        while self.app.is_scrolling:
            rotated_text = original_text
            for i in range(text_length):
                rotated_text = original_text[i:] + original_text[:i]
                self.displayed_text.set(rotated_text)
                time.sleep(0.1 / self.app.scroll_speed.get())  # Ajuste na velocidade

    def destroy(self):
        # Função para destruir a segunda janela
        self.app.stop_text()
        super().destroy()


def get_monitors():
    # Função para obter informações sobre monitores
    try:
        from screeninfo import get_monitors
        return get_monitors()
    except ImportError:
        print("A biblioteca 'screeninfo' não está instalada. Instale-a para melhor suporte a monitores múltiplos.")
        return []


if __name__ == "__main__":
    root = tk.Tk()
    app = ScrollingTextApp(root)
    root.mainloop()
