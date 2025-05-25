import tkinter as tk
from database import search_ocpd


class SearchOCPD:
    def __init__(self, root):
        self.root = root
        self.root.title("Поиск кода ОКПД2")

        self.window_color = "#B8B799"
        self.root.config(bg=self.window_color)
        self.root.resizable(False, False)

        # Создание рамки
        self.frame = tk.Frame(self.root, bg=self.window_color)
        self.frame.pack(padx=5, pady=5)

        # Поле для ввода данных
        self.input_label = tk.Label(self.frame, text="Поиск ОКПД2", bg=self.window_color)
        self.input_label.pack()

        self.input_entry = tk.Entry(self.frame)
        self.input_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Кнопка для обновления Label
        self.update_button = tk.Button(self.frame, text="Поиск", bg="#99FFFF", command=self.update_label)
        self.update_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.canvas = tk.Canvas(self.frame, width=600, height=400, bg=self.window_color)
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side="right", fill="y")

        # Конфигурация прокрутки
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.canvas.yview)

        # Создание внутренней рамки для содержимого
        self.inner_frame = tk.Frame(self.canvas, bg=self.window_color)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')

    def show_links(self, links):
        # Очистка предыдущего содержимого
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        # Создание нового списка ссылок
        for idx, link in enumerate(links):
            link_button = tk.Button(self.inner_frame, text=link[0], fg="blue", bg=self.window_color, relief="flat",
                                    cursor="hand2",
                                    command=lambda index=link[0]: self.update_links(index))

            link_button.grid(row=idx, column=0, padx=5, pady=5)

            descr = tk.Label(self.inner_frame, bg=self.window_color)
            descr.config(text=link[1], wraplength=500, justify="left")
            descr.grid(row=idx, column=1, padx=10, pady=10, sticky="w")

        self.inner_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_links(self, index):
        res = search_ocpd(index)
        self.show_links(res)

    def update_label(self):
        # Получение введенных данных
        data = self.input_entry.get()
        if data:
            result = search_ocpd(data)
            self.show_links(result)
