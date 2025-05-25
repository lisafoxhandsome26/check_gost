from os import walk, remove
from typing import List, Any
from docx import Document
from database import Filenames, insert_data, insert_new_gost


documents = ["ГОСТ ", "ТР ТС", "СанПи", "СНиП ", "СП", "ТР ЕА"]


def check_table(tables: Any) -> Any:
    """Функция для нахождения нужной таблицы в файле"""
    for table in tables:
        d = [True for row in table.rows[1:][:5] if row.cells[0].text[:5] in documents]
        if len(d) == 5:
            return table


def read_docx_tables(file_path: str) -> List[tuple]:
    """Функция для чтения файла"""
    doc = Document(file_path)
    data_table = []
    tables = doc.tables
    table_good = check_table(tables)
    if table_good:
        for row in table_good.rows[1:]:
            gost: str = row.cells[0].text.strip().replace("\n", "")
            text: str = row.cells[1].text.strip().replace("\n", "")
            if len(gost) > 5 and gost != text and len(text) > 10 and gost[-1].isdigit():
                data_table.append(
                    (gost, text)
                )
        obj = Filenames(filename=file_path, status=True)
    else:
        obj = Filenames(filename=file_path, status=False)

    insert_data(obj)
    return data_table


def remove_duplicates(array: List[tuple]) -> List[tuple]:
    """Наивный алгоритм удаления дубликатов"""
    length = len(array)
    i = 0
    while i < length:
        found = False
        for k in range(i+1, length):
            if array[k][0] == array[i][0]:
                found = True
                break
        if not found:
            i += 1
            continue
        else:
            array.remove(array[i])
        length -= 1
    return array


def find_file(path_to_project: str) -> None:
    """Функция для поиска файла"""
    ready_data = []
    for dirpath, dirnames, filenames in walk(path_to_project):
        for f in filenames:
            if f[:9] == 'Проект ТУ':
                file_path = dirpath + '/' + f
                if file_path.endswith('.docx'):
                    data = read_docx_tables(file_path)
                    ready_data.extend(data)

    for table in sorted(remove_duplicates(ready_data)):
        doc = table[0]
        descr = table[1]
        insert_new_gost(doc, descr)
