from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from core.config import settings
from core.utils.case_convertor import camel_case_to_snake_case


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=settings.db.naming_convention)

    id: Mapped[int] = mapped_column(primary_key=True)

    @declared_attr
    def __tablename__(cls):  # noqa
        return f"{camel_case_to_snake_case(cls.__name__)}"
