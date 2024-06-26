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
    rls: Mapped[int] = mapped_column(Integer, nullable=True, comment="release")
    kw: Mapped[str] = mapped_column(String(250), nullable=True, comment="keyword")

    pubs: Mapped[list["PUB"]] = relationship("PUB", secondary="pdf_pub", back_populates="pdf", uselist=True)
    tags: Mapped[list["TAG"]] = relationship("TAG", secondary="pdf_tag", back_populates="pdf", uselist=True)

    def __repr__(self):
        return (
            f"<PDF(fp='{self.fp}', title='{self.tit}', number='{self.num}',"
            f" release='{self.rls}')>"
            f" publisher='{self.pubs}'"
            f" tag='{self.tags}'"
        )

    @property
    def name(self):
        return os.path.basename(self.fp)


class TAG(Base):  # TAG表
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="ID")
    tag: Mapped[str] = mapped_column(String(250), nullable=False, unique=True, comment="tag")
    kw: Mapped[str] = mapped_column(String(250), nullable=True, comment="keyword")

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


class PUB(Base):
    __tablename__ = "pub"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="ID")
    pub: Mapped[str] = mapped_column(String(250), nullable=False, unique=True, comment="publisher")
    kw: Mapped[str] = mapped_column(String(250), nullable=True, comment="keyword")

    pdf: Mapped[list["PDF"]] = relationship("PDF", secondary="pdf_pub", back_populates="pubs", uselist=True)

    def __repr__(self):
        return f"<PUB({self.pub})>"


class PDF_PUB(Base):
    __tablename__ = "pdf_pub"
    __table_args__ = (
        ForeignKeyConstraint(["pdf_id"], ["pdf.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["pub_id"], ["pub.id"], ondelete="CASCADE"),
        UniqueConstraint("pdf_id", "pub_id", name="pdf_pub_pdf_id_pub_id_uc"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="ID")
    pdf_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="pdf ID")
    pub_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="publisher ID")
