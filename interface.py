import tkinter as tk
from tkinter.ttk import Combobox
from tkinter import messagebox
from typing import Callable
import re
from os.path import isdir, isfile

from writer import find_file
from parser_file import extract_gosts, pattern
from database import init_database, insert_new_gost, update_gost_descr, delete_gost, check_gost_in_db
from utils import get_request
from main_file import SearchOCPD

main_color = "#E5FFCC"


def interface_two_param(one_param: str, two_param: str, func_to_run: Callable) -> None:
    tk.Label(input_frame, text=one_param, bg=main_color).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(input_frame, text=two_param, bg=main_color).grid(row=1, column=0, padx=10, pady=10)
    get_data_1 = tk.Entry(input_frame, width=100)
    get_data_2 = tk.Entry(input_frame, width=100)
    get_data_1.grid(row=0, column=1, padx=10, pady=10)
    get_data_2.grid(row=1, column=1, padx=10, pady=10)
    submit_button = tk.Button(input_frame,
                              text="Выполнить",
                              bg="#FFFF66",
                              padx=7,
                              pady=7,
                              command=lambda: func_to_run(get_data_1.get(), get_data_2.get()))
    submit_button.grid(row=2, columnspan=2, pady=10)


def interface_one_param(one_param: str, func_to_run: Callable) -> None:
    tk.Label(input_frame,
             text=one_param,
             bg=main_color
             ).grid(row=0, column=0, padx=10, pady=10)
    get_data_1 = tk.Entry(input_frame, width=100)
    get_data_1.grid(row=0, column=1, padx=10, pady=10)
    submit_button = tk.Button(input_frame,
                              text="Выполнить",
                              bg="#FFFF66",
                              padx=7,
                              pady=7,
                              command=lambda: func_to_run(get_data_1.get()))
    submit_button.grid(row=2, columnspan=2, pady=10)


def interface(one_param: str, text_area, func_to_run: Callable):
    tk.Label(input_frame,
             text=one_param,
             bg=main_color
             ).grid(row=0, column=0, padx=10, stick="w", pady=10)
    combobox = Combobox(input_frame, values=["Русский", "Английский"])
    combobox.grid(row=0, column=1, padx=10, stick="w", pady=10)
    submit_button = tk.Button(input_frame,
                              text="Выполнить",
                              bg="#FFFF66",
                              padx=7,
                              pady=7,
                              command=lambda: func_to_run(combobox.get(), text_area))

    submit_button.grid(row=0, column=2, stick="w", pady=5)


def show_form(action: str) -> None:
    # Удаление виджетов
    for widget in input_frame.winfo_children():
        widget.destroy()
        lable_gost.config(text="")
    text_area = tk.Text(input_frame, height=10)
    # Создание формы ввода в зависимости от действия
    if action == "add":  # 2 Параметра Новый ГОСТ и описание
        interface_two_param(one_param="Новый НД:", two_param="Название НД:", func_to_run=add_gost)

    elif action == "edit":  # 2 Параметра Изменяемый ГОСТ и новое описание
        interface_two_param(one_param="Обновляемый НД", two_param="Название НД", func_to_run=edit_gost)

    elif action == "delete":  # 1 Параметр Удаляемый ГОСТ
        interface_one_param(one_param="Удаляемый НД", func_to_run=delete_gost_from_db)

    elif action == "create_table":  # 1 Параметр путь к файлу
        interface_one_param(one_param="Путь к файлу:", func_to_run=create_table)

    elif action == "ocpd":  # 1 Параметр путь к файлам
        run_search_ocpd()

    elif action == "inform":
        interface_one_param(one_param="Введите ГОСТ:", func_to_run=get_gost)


def run_search_ocpd():
    new_window = tk.Toplevel(root)
    app = SearchOCPD(new_window)
    new_window.grab_set()


def add_gost(gost: str, descr: str):
    try:
        result: tuple = check_gost_in_db(gost)
        gosts: list = re.findall(pattern, gost)

        if gosts and descr and result is None:
            insert_new_gost(gost, descr)
            messagebox.showinfo("Информация", f"{gost} добавлен.")
        else:
            messagebox.showerror("Ошибка", f"Введите нормальный НД {gost}.")
    except BaseException as e:
        messagebox.showerror("Ошибка", f"Не удалось добавить {gost} {e}.")


def delete_gost_from_db(gost: str):
    try:
        if check_gost_in_db(gost):
            delete_gost(gost)
            messagebox.showinfo("Информация", f"{gost} успешно удален.")
        else:
            messagebox.showerror("Ошибка", f"Возможно {gost} написано с ошибкой или не существует в БД")
    except BaseException as e:
        messagebox.showerror("Ошибка", f"Не удалось удалить {gost} {e}.")


def edit_gost(old_gost: str, new_desr: str):
    try:
        if check_gost_in_db(old_gost):
            update_gost_descr(old_gost, new_desr)
            messagebox.showinfo("Информация", f"{old_gost} изменен.")
        else:
            messagebox.showerror("Ошибка", f"Возможно {old_gost} написан с ошибкой или не существует в БД")
    except BaseException as e:
        messagebox.showerror("Ошибка", f"Не удалось обновить {old_gost} {e}")


def create_table(path_to_file: str):
    try:
        if isfile(path_to_file):
            extract_gosts(path_to_file)
            messagebox.showinfo("Информация", f"Таблица создана.")
        else:
            messagebox.showerror("Ошибка", f"Указанный путь к файлу {path_to_file} не существует.")
    except BaseException as e:
        messagebox.showerror("Ошибка", f"Во время записи таблицы произошла ошибка {e}")


def update_db(path_to_files: str):
    try:
        if isdir(path_to_files):
            init_database()
            find_file(path_to_files)
            messagebox.showinfo("Информация", "База данных обновлена.")
        else:
            messagebox.showerror("Ошибка", f"Указанный путь к директоии {path_to_files} не существует.")
    except BaseException as e:
        messagebox.showerror("Ошибка", f"Обновить БД не удалось {e}")


def get_gost(gost: str):
    try:
        gosts = re.findall(fr'[^a-zA-Zа-яА-Я]', gost)
        preper = ''.join(gosts).strip()
        result = get_request([preper])
        if result:
            text = ""
            for col in result[:8]:
                text += f"{col[0]} {col[2]}\n{col[1]}\n\n"
            lable_gost.config(text=text,
                              wraplength=1000,
                              bg=main_color,
                              font=("Arial", 11),
                              justify="left")
            lable_gost.pack(padx=5, pady=10)
    except BaseException as e:
        messagebox.showerror("Ошибка", f"Не удалось найти {gost} {e}")


# Создание основного окна
root = tk.Tk()
root.title("Помошник для работы с ГОСТ")
root.config(bg=main_color)

# Фрейм для кнопок действий
button_frame = tk.Frame(root, bg=main_color)
button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

# Создание кнопок
tk.Button(button_frame, text="Добавить новый ГОСТ", command=lambda: show_form("add"), bg="#99FF99").pack(side=tk.LEFT,
                                                                                                         padx=5)
tk.Button(button_frame, text="Удалить ГОСТ", command=lambda: show_form("delete"), bg="#FF9999").pack(side=tk.LEFT,
                                                                                                     padx=5)
tk.Button(button_frame, text="Изменить ГОСТ", command=lambda: show_form("edit"), bg="#FFCC99").pack(side=tk.LEFT,
                                                                                                    padx=5)
tk.Button(button_frame, text="Создать таблицу", command=lambda: show_form("create_table"),
          bg="#99FFFF").pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="ОКПД2", command=lambda: show_form("ocpd"), bg="#FF9999").pack(side=tk.LEFT,
                                                                                                       padx=5)
tk.Button(button_frame, text="Посмотреть информацию о ГОСТ", command=lambda: show_form("inform"),
          bg="#99FFFF").pack(side=tk.LEFT, padx=5)

# Фрейм для ввода данных
input_frame = tk.Frame(root, bg=main_color)
input_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=30)


lable_gost = tk.Label(root)

# Запуск основного цикла
root.mainloop()
