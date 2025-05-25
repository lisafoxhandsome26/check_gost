from re import findall
from typing import Any
from sqlalchemy import create_engine, select, update, delete, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from utils import get_request
from docx import Document

engine = create_engine('sqlite:///documents.db')
session = sessionmaker(bind=engine)
Base = declarative_base()


class Documents(Base):
    __tablename__ = "gosts"

    id: Mapped[int] = mapped_column(primary_key=True)
    document: Mapped[str]
    descr: Mapped[str]


class Reglaments(Base):
    __tablename__ = "reglaments"

    id: Mapped[int] = mapped_column(primary_key=True)
    document: Mapped[str]
    descr: Mapped[str]


class BuilderDoc(Base):
    __tablename__ = "builder_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    document: Mapped[str]
    descr: Mapped[str]


class AnotherDoc(Base):
    __tablename__ = "another_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    document: Mapped[str]
    descr: Mapped[str]


class Filenames(Base):
    __tablename__ = "filenames"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str]
    status: Mapped[bool]


class OkpdClasificator(Base):
    __tablename__ = "classificator_ocpd"

    id: Mapped[int] = mapped_column(primary_key=True)
    ocpd: Mapped[str]
    description: Mapped[str]


def make_data_okpd2(file_path):
    """Функция для добавления кодов ОКПД2"""
    doc = Document(file_path)
    tables = doc.tables
    last_data = []
    for table in tables:
        for row in table.rows:
            ocpd2: str = row.cells[0].text.strip().replace("\n", "")
            description: str = row.cells[1].text.strip().replace("\n", "")
            if ocpd2 and ocpd2[0].isdigit():
                print(ocpd2, description)
                last_data.append(OkpdClasificator(ocpd=ocpd2, description=description))

    with session() as sos:
        sos.add_all(last_data)
        sos.commit()


def search_ocpd(cod: str) -> list[tuple]:
    """Функция для поиска кодов ОКПД2"""
    if cod[0].isdigit():
        c = 5 if len(cod) == 8 else 3
        stmt = select(OkpdClasificator).where(
            OkpdClasificator.ocpd.like(f'{cod}%'),
            func.length(OkpdClasificator.ocpd) < func.length(f'{cod}') + c)
    else:
        stmt = select(OkpdClasificator).where(OkpdClasificator.description.like(f'%{cod}%'))

    with session() as sos:
        result = sos.execute(stmt).scalars().all()

    return [(row.ocpd, row.description) for row in result]


def init_database() -> None:
    """Функция для инициализации БД"""
    with session() as sos:
        try:
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
        finally:
            sos.rollback()
            sos.commit()


def insert_data(obj: Any) -> None:
    """Функция для добавления данных в БД"""
    with session() as sos:
        sos.add(obj)
        sos.commit()


def remove_gost(obj: Any, gost: str) -> None:
    """Функция для удаления данных в БД"""
    stm = delete(obj).where(obj.document == gost)
    with session() as sos:
        sos.execute(stm)
        sos.commit()


def select_data(obj: Any, substring: str) -> tuple[str, str]:
    """Функция для выборки данных"""
    with session() as sos:
        stmt = select(obj).where(obj.document.like(f'%{substring}%'))
        result = sos.execute(stmt).scalars().first()
        if result:
            return result.document, result.descr
        else:
            gosts = findall(fr'[^a-zA-Zа-яА-Я]', substring)
            preper = ''.join(gosts).strip()
            result = get_request([preper])
            if result:
                status = "Неизвестен"
                descr = "Описания не существует"
                for gost in result:
                    if len(gost) == 3:
                        doc, descr, status = gost[0], gost[1], gost[2]
                    if status in ["Действует", "Принят", "Действует только в РФ"]:
                        insert_new_gost(doc, descr)
                        return doc, descr
                return substring, f"{status} {descr}"
            return substring, ""


def select_check(obj: Any, substring: str) -> str:
    """Функция для выборки данных"""
    with session() as sos:
        stmt = select(obj).where(obj.document == substring)
        result = sos.execute(stmt).scalars().first()
        if result:
            return result.document


def update_data(obj: Any, gost: str, descr: str) -> None:
    """Функция для обновления данных в БД"""
    with session() as sos:
        data: str = select_check(obj, gost)
        if data:
            stm = update(obj).where(obj.document == gost).values(descr=descr)
            sos.execute(stm)
            sos.commit()


def insert_new_gost(gost: str, descr: str) -> None:
    """Функция для вставки нового НД"""
    if gost[:5] == "ТР ТС" or gost[:5] == "ТР ЕА":
        obj = Reglaments(document=gost, descr=descr)
        insert_data(obj)
    elif gost[:4] == "ГОСТ":
        obj = Documents(document=gost, descr=descr)
        insert_data(obj)
    elif gost[:5] in ["СанПи", "СНиП "] or gost[:2] == "СП":
        obj = BuilderDoc(document=gost, descr=descr)
        insert_data(obj)
    else:
        obj = AnotherDoc(document=gost, descr=descr)
        insert_data(obj)


def update_gost_descr(gost: str, descr: str) -> None:
    """Функция для обновления НД"""
    if gost[:5] == "ТР ТС" or gost[:5] == "ТР ЕА":
        update_data(Reglaments, gost, descr)
    elif gost[:4] == "ГОСТ":
        update_data(Documents, gost, descr)
    elif gost[:5] in ["СанПи", "СНиП "] or gost[:2] == "СП":
        update_data(BuilderDoc, gost, descr)
    else:
        update_data(AnotherDoc, gost, descr)


def delete_gost(gost: str) -> None:
    """Функция для удаления НД"""
    if gost[:5] == "ТР ТС" or gost[:5] == "ТР ЕА":
        remove_gost(Reglaments, gost)
    elif gost[:4] == "ГОСТ":
        remove_gost(Documents, gost)
    elif gost[:5] in ["СанПи", "СНиП "] or gost[:2] == "СП":
        remove_gost(BuilderDoc, gost)
    else:
        remove_gost(AnotherDoc, gost)


def check_gost_in_db(gost: str):
    """Функция для удаления НД"""
    if gost[:5] == "ТР ТС" or gost[:5] == "ТР ЕА":
        return select_check(Reglaments, gost)
    elif gost[:4] == "ГОСТ":
        return select_check(Documents, gost)
    elif gost[:5] in ["СанПи", "СНиП "] or gost[:2] == "СП":
        return select_check(BuilderDoc, gost)
    else:
        return select_check(AnotherDoc, gost)
