import os
import datetime
import zipfile

from sqlalchemy.orm import Session

from core import model


def scan_pdf(folder: str) -> list | None:
    disk_path = [chr(i) + ":/" for i in range(ord("A"), ord("Z") + 1)]
    disk_path.append("/")
    if folder.upper() in disk_path:
        return None
    paths = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".pdf"):
                paths.append(os.path.join(root, file).replace("\\", "/"))
    return paths


def zip_path(paths: list[str], folder: str) -> None:
    folder = os.path.join(folder, "PDF_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".zip")
    zip_file = zipfile.ZipFile(folder, "w", zipfile.ZIP_DEFLATED)
    for path in paths:
        zip_file.write(path, os.path.basename(path))
    zip_file.close()


def create_pdf_by_path(session: Session, path: str) -> model.PDF:
    pdf = model.PDF(fp=path)
    session.add(pdf)
    session.commit()
    return pdf


def get_pdf_by_path(session: Session, path: str) -> model.PDF | None:
    return session.query(model.PDF).filter(model.PDF.fp == path).one_or_none()


def get_tag_by_tag(session: Session, tag: str) -> model.TAG:
    if not (t := session.query(model.TAG).filter(model.TAG.tag == tag).one_or_none()):
        t = model.TAG(tag=tag)
        session.add(t)
        session.commit()
    return t


def get_all_pub(session: Session) -> list:
    return [i[0] for i in session.query(model.PDF.pub).distinct().order_by(model.PDF.pub) if i[0]]


def get_all_rls(session: Session) -> list:
    return [i[0] for i in session.query(model.PDF.rls).distinct().order_by(model.PDF.rls) if i[0]]


def get_all_tag(session: Session) -> list:
    return [i[0] for i in session.query(model.TAG.tag).distinct().order_by(model.TAG.tag) if i[0]]


def get_pdf_by_filters(session: Session, pub: list, rls: list, tag: list) -> list:
    return (
        session.query(model.PDF)
        .filter(
            model.PDF.pub.in_(pub) if pub else True,
            model.PDF.rls.in_(rls) if rls else True,
            model.PDF.tags.any(model.TAG.tag.in_(tag)) if tag else True,
        )
        .all()
    )


def update_pdf_with_field(session: Session, pdf: model.PDF, field: str, data: any) -> None:
    setattr(pdf, field, data)
    session.add(pdf)
    session.commit()


def delete_pdf(session: Session, pdf: model.PDF) -> None:
    session.delete(pdf)
    session.commit()


def clear_tag_if_unused(session: Session) -> None:
    for tag in session.query(model.TAG).all():
        if not tag.pdf:
            session.delete(tag)
    session.commit()
