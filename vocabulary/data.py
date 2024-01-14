import json
import random
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Tuple

from rich.console import Console
from rich.table import Table

VocabularyStr = str
DatetimeStr = str
VocabularyStateInt = int
VocabularyTuple = Tuple[VocabularyStr, DatetimeStr, VocabularyStateInt]
VocabularyTupleList = List[VocabularyTuple]


class VocabularyState(int, Enum):
    FORGOT: int = 1
    READ: int = 2


def sort_by_date(row: VocabularyTuple):
    date = row[1]
    return datetime.strptime(date, r"%Y-%m-%dT%H:%M:%S.%f")


def get_rows(rows: VocabularyTupleList, num: int = 10, forgot: bool = False):
    if forgot:
        i = j = 0
        new_rows = []
        total = len(rows)
        while i < num and j < total:
            row = rows[j]
            if row[2] == VocabularyState.FORGOT.value:
                new_rows.append(row)
                i += 1
            j += 1
    else:
        new_rows = rows[:num]
    return new_rows


def print_rows(rows: VocabularyTupleList):
    table = Table()
    table.add_column("vocabulary")
    table.add_column("date")
    table.add_column("state")

    for row in rows:
        vocabulary = row[0]
        date = row[1]
        state_code = row[2]
        if state_code == VocabularyState.FORGOT.value:
            state = "forgot"
        else:
            state = "read"
        table.add_row(vocabulary, date, state)

    console = Console()
    console.print(table)


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
            self.last_viewed.append((v, rows[-1][0], rows[-1][1]))
        self.last_viewed.sort(key=sort_by_date)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
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

    def list(self, num: int = 10, forgot: bool = False):
        rows = get_rows(self.last_viewed, num=num, forgot=forgot)
        print_rows(rows)

    def new(self, num: int = 10):
        rows = self.last_viewed[-1 - num :]
        print_rows(rows)

    def random(self, num: int = 10, forgot: bool = False):
        random.shuffle(self.last_viewed)
        return self.list(num=num, forgot=forgot)

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

    def delete(self, vocabulary: str):
        self.data.pop(vocabulary)
        self.data.pop(vocabulary)
