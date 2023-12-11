import os

from sqlalchemy.orm import Session

from core import model


def scan_pdf(folder: str) -> list | None:
    disk_path = [chr(i) + ':/' for i in range(ord('A'), ord('Z') + 1)]
    disk_path.append('/')
    if folder.upper() in disk_path:
        return None
    paths = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                paths.append(os.path.join(root, file).replace('\\', '/'))
    return paths


def get_pdf_by_path(session: Session, path: str) -> model.PDF | None:
    return session.query(model.PDF).filter(model.PDF.fp == path).one_or_none()


def create_pdf_by_path(session: Session, path: str) -> model.PDF:
    pdf = model.PDF(fp=path)
    session.add(pdf)
    session.commit()
    return pdf


def update_pdf_with_field(session: Session, pdf: model.PDF, field: str, data: any) -> None:
    setattr(pdf, field, data)
    session.add(pdf)
    session.commit()


def get_tag_by_tag(session: Session, tag: str) -> model.TAG:
    if not (t := session.query(model.TAG).filter(model.TAG.tag == tag).one_or_none()):
        t = model.TAG(tag=tag)
        session.add(t)
        session.commit()
    return t
