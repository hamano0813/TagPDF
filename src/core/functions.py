import os
import csv
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


def zip_path(paths: list[str], folder: str, session: Session) -> None:
    folder = os.path.join(folder, "PDF_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".zip")
    zip_file = zipfile.ZipFile(folder, "w", zipfile.ZIP_DEFLATED)
    csv_path = folder.replace("PDF_", "INFO_").replace(".zip", ".csv")
    csv_file = open(csv_path, "w", encoding="gbk")
    csv_writer = csv.writer(csv_file, lineterminator='\n')
    csv_writer.writerow(["序号", "标题", "文号", "发布单位", "发布日期"])
    for rid, path in enumerate(paths):
        pdf: model.PDF = get_pdf_by_path(session, path)
        info = [rid+1, pdf.tit]
        info.append(pdf.num if pdf.num else " ")
        if pdf.pubs:
            info.append("、".join([p.pub for p in pdf.pubs]))
        info.append(pdf.rls if pdf.rls else " ")
        csv_writer.writerow(info)
        zip_file.write(path, os.path.basename(path))
    csv_file.close()
    zip_file.close()


def rename_pdfs(session: Session):
    pdfs: list[model.PDF] = get_pdf_by_filters(session, [], [], [])
    for pdf in pdfs:
        if not os.path.exists(pdf.fp):
            continue
        title = pdf.tit
        for i in ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]:
            title = title.replace(i, "")
        title += '.pdf'
        root, name = os.path.split(pdf.fp)
        if name != title:
            try:
                os.rename(pdf.fp, path:=os.path.join(root, title))
                pdf.fp = path
                session.add(pdf)
            except PermissionError as e:
                return pdf.fp
            finally:
                session.commit()


def create_pdf_by_path(session: Session, path: str) -> model.PDF:
    pdf = model.PDF(fp=path)
    session.add(pdf)
    session.commit()
    return pdf


def get_pdf_by_path(session: Session, path: str) -> model.PDF | None:
    return session.query(model.PDF).filter(model.PDF.fp == path).one_or_none()


def get_pub_by_pub(session: Session, pub: str) -> model.PUB:
    if not (p := session.query(model.PUB).filter(model.PUB.pub == pub).one_or_none()):
        p = model.PUB(pub=pub)
        session.add(p)
        session.commit()
    return p      


def get_tag_by_tag(session: Session, tag: str) -> model.TAG:
    if not (t := session.query(model.TAG).filter(model.TAG.tag == tag).one_or_none()):
        t = model.TAG(tag=tag)
        session.add(t)
        session.commit()
    return t


def get_all_rls(session: Session) -> list:
    return [i[0] for i in session.query(model.PDF.rls).distinct().order_by(model.PDF.rls) if i[0]]


def get_all_pub(session: Session) -> list:
    return [i[0] for i in session.query(model.PUB.pub).distinct().order_by(model.PUB.pub) if i[0]]


def get_all_tag(session: Session) -> list:
    return [i[0] for i in session.query(model.TAG.tag).distinct().order_by(model.TAG.tag) if i[0]]


def get_pdf_by_filters(session: Session, pub: list, rls: list, tag: list) -> list:
    print(pub, rls, tag)
    return (
        session.query(model.PDF)
        .filter(
            model.PDF.pubs.any(model.PUB.pub.in_(pub)) if pub else True,
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


def clear_pub_if_unused(session: Session) -> None:
    for pub in session.query(model.PUB).all():
        if not pub.pdf:
            session.delete(pub)
    session.commit()


def clear_tag_if_unused(session: Session) -> None:
    for tag in session.query(model.TAG).all():
        if not tag.pdf:
            session.delete(tag)
    session.commit()
