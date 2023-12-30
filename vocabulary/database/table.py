from datetime import datetime
from enum import Enum
from typing import List

from sqlalchemy import (
    TIMESTAMP,
    VARCHAR,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import validates
from sqlalchemy.sql import functions as func

from vocabulary.database.base import Base

datetime_format_db = r"%Y-%m-%dT%H:%M:%S.%f"
datetime_format = r"%Y-%m-%dT%H:%M:%S.%f%z"
datetime_format_no_f = r"%Y-%m-%dT%H:%M:%S%z"
datetime_formats = [datetime_format_db, datetime_format, datetime_format_no_f]


def iso2datetime(date: str, formats: List[str] = datetime_formats) -> datetime:
    for f in formats:
        try:
            return datetime.strptime(date, f)
        except ValueError:
            pass
    raise ValueError(f"time data {date} does not match any format")


class Vocabulary(Base):
    __tablename__: str = "vocabulary"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARCHAR(128), nullable=False, index=True, unique=True)


class VocabularyState(int, Enum):
    FORGOT: int = 1
    REMEMBERED: int = 2
    READ: int = 3


class VocabularyDate(Base):
    __tablename__: str = "vocabulary_date"
    id = Column(Integer, primary_key=True, index=True)
    v_id = Column(
        Integer,
        ForeignKey("vocabulary.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    state = Column(Integer, index=True, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)

    @validates("timestamp")
    def validate_timestamp(self, _, value):
        if type(value) is str:
            return iso2datetime(value)
        return value


class CrudVocabulary:
    async def add(vocabulary: str):
        ...
