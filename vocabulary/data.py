import json
import random
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.table import Table

VocabularyStr = str
DatetimeStr = str
VocabularyStateInt = int
VocabularyCount = int
VocabularyTuple = Tuple[VocabularyStr, DatetimeStr, VocabularyStateInt, VocabularyCount]
VocabularyTupleList = List[VocabularyTuple]


class VocabularyState(int, Enum):
    FORGOT: int = 1
    READ: int = 2


datetime_format_db = r"%Y-%m-%dT%H:%M:%S.%f"
datetime_format = r"%Y-%m-%dT%H:%M:%S.%f%z"
datetime_format_no_f = r"%Y-%m-%dT%H:%M:%S%z"
datetime_formats = [datetime_format_db, datetime_format, datetime_format_no_f]


def get_datetime(date: str) -> Optional[datetime]:
    for f in datetime_formats:
        try:
            return datetime.strptime(date, f)
        except ValueError:
            pass
    return None


def sort_by_date(row: VocabularyTuple):
    date = row[1]
    return datetime.strptime(date, r"%Y-%m-%dT%H:%M:%S.%f")


def get_rows(
    rows: VocabularyTupleList, num: int = 10, forgot: bool = False, le: int = None
):
    i = j = 0
    new_rows = []
    total = len(rows)
    while i < num and j < total:
        row = rows[j]
        is_forgot = not forgot or (row[2] == VocabularyState.FORGOT.value)
        is_le = le is None or (row[3] <= le)
        if all([is_forgot, is_le]):
            new_rows.append(row)
            i += 1
        j += 1
    return new_rows


def print_rows(rows: VocabularyTupleList):
    table = Table()
    table.add_column("No.")
    table.add_column("Vocabulary")
    table.add_column("Date")
    table.add_column("Count")
    table.add_column("State")

    for i, row in enumerate(rows):
        vocabulary = row[0]
        date = row[1]
        state_code = row[2]
        count = str(row[3])
        if state_code == VocabularyState.FORGOT.value:
            state = "forgot"
        else:
            state = "read"
        no = str(i + 1)
        table.add_row(no, vocabulary, date, count, state)

    console = Console()
    console.print(table)


def saved(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        args[0]._save = True
        return f(*args, **kwargs)

    return wrap


class VocabularyData:
    def __init__(self, fpath: str = "./vocabulary.json"):
        self._fpath = Path(fpath)
        if self._fpath.exists():
            with self._fpath.open(mode="r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

        self.last_viewed: VocabularyTupleList = []
        for v, rows in self.data.items():
            self.last_viewed.append((v, rows[-1][0], rows[-1][1], len(rows)))
        self.last_viewed.sort(key=sort_by_date)

        self.first_viewed: VocabularyTupleList = []
        for v, rows in self.data.items():
            self.first_viewed.append((v, rows[0][0], rows[0][1], len(rows)))
        self.first_viewed.sort(key=sort_by_date)

        self._save = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._save:
            return
        with self._fpath.open(mode="w") as f:
            json.dump(self.data, f, indent=4)

    def info(self, vocabulary: str):
        rows = self.data.get(vocabulary, None)
        if rows is None:
            return

        table = Table(title=vocabulary)
        table.add_column("date")
        table.add_column("state")

        for row in rows:
            date = row[0]
            state_code = row[1]
            if state_code == VocabularyState.FORGOT.value:
                state = "forgot"
            else:
                state = "read"
            table.add_row(date, state)

        console = Console()
        console.print(table)

    def list(self, num: int = 10, forgot: bool = False, le: int = None):
        rows = get_rows(self.last_viewed, num=num, forgot=forgot, le=le)
        print_rows(rows)

    def new(self, num: int = 10):
        rows = self.first_viewed[-num:]
        print_rows(rows)

    def random(self, num: int = 10, forgot: bool = False):
        random.shuffle(self.last_viewed)
        return self.list(num=num, forgot=forgot)

    @saved
    def read(self, vocabulary: str, state: VocabularyState):
        if type(state) is VocabularyState:
            state = state.value
        row = (datetime.now().isoformat(), state)
        if self.data.get(vocabulary, None) is None:
            self.data[vocabulary] = [row]
        else:
            self.data[vocabulary].append(row)

    def status(self):
        total = len(self.last_viewed)
        console = Console()
        console.print(f"total: {total}")

    def today(self):
        rows = []
        for row in self.first_viewed:
            date = get_datetime(row[1])
            if date is None:
                continue
            if date.date() >= datetime.today().date():
                rows.append(row)
        print_rows(rows)

    @saved
    def delete(self, vocabulary: str):
        self.data.pop(vocabulary)
        self.data.pop(vocabulary)
