import os

from sqlalchemy import Integer, String, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):  # 基类
    pass


class PDF(Base):  # PDF表
    __tablename__ = "pdf"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="ID")
    fp: Mapped[str] = mapped_column(String(250), nullable=True, unique=True, comment="file path")
    tit: Mapped[str] = mapped_column(String(250), nullable=True, comment="title")
    num: Mapped[str] = mapped_column(String(250), nullable=True, comment="number")
    pub: Mapped[str] = mapped_column(String(250), nullable=True, comment="publisher")
    rls: Mapped[int] = mapped_column(Integer, nullable=True, comment="release")

    tags: Mapped[list["TAG"]] = relationship("TAG", secondary="pdf_tag", back_populates="pdf", uselist=True)

    def __repr__(self):
        return (
            f"<PDF(fp='{self.fp}', title='{self.tit}', number='{self.num}',"
            f" publisher='{self.pub}', release='{self.rls}')>"
            f" tag='{self.tags}'>"
        )

    @property
    def name(self):
        return os.path.basename(self.fp)


class TAG(Base):  # TAG表
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="ID")
    tag: Mapped[str] = mapped_column(String(250), nullable=False, unique=True, comment="tag")

    pdf: Mapped[list["PDF"]] = relationship("PDF", secondary="pdf_tag", back_populates="tags", uselist=True)

    def __repr__(self):
        return f"<TAG({self.tag})>"


class PDF_TAG(Base):  # PDF_TAG表
    __tablename__ = "pdf_tag"
    __table_args__ = (
        ForeignKeyConstraint(["pdf_id"], ["pdf.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["tag_id"], ["tag.id"], ondelete="CASCADE"),
        UniqueConstraint("pdf_id", "tag_id", name="pdf_tag_pdf_id_tag_id_uc"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="ID")
    pdf_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="pdf ID")
    tag_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="tag ID")
