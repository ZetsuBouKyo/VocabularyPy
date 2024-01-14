#!.venv/bin/python3

from typing import List

from typer import Argument, Option

from lib.typer import CustomTyper
from vocabulary.data import VocabularyData, VocabularyState

app = CustomTyper(rich_markup_mode="rich")


@app.command()
def read(vocabulary: str = Argument(...)):
    with VocabularyData() as data:
        data.read(vocabulary, state=VocabularyState.READ.value)


@app.command()
def forgot(vocabulary: str = Argument(...)):
    with VocabularyData() as data:
        data.read(vocabulary, state=VocabularyState.FORGOT.value)


@app.command()
def new(number: int = Option(10, "-n/")):
    with VocabularyData() as data:
        data.new(num=number)


@app.command()
def random(number: int = Option(10, "-n/"), forgot: bool = Option(False, "-f/")):
    with VocabularyData() as data:
        data.random(num=number, forgot=forgot)


@app.command()
def delete(vocabulary: List[str] = Option([], "-v/")):
    with VocabularyData() as data:
        for v in vocabulary:
            data.delete(v)


@app.command()
def list(
    vocabulary: str = Option(None, "-v/"),
    number: int = Option(10, "-n/"),
    forgot: bool = Option(False, "-f/"),
):
    if vocabulary is not None:
        with VocabularyData() as data:
            data.info(vocabulary)
    else:
        with VocabularyData() as data:
            data.list(num=number, forgot=forgot)


@app.command()
def list(
    vocabulary: str = Option(None, "-v/"),
    number: int = Option(10, "-n/"),
    forgot: bool = Option(False, "-f/"),
):
    if vocabulary is not None:
        with VocabularyData() as data:
            data.info(vocabulary)
    else:
        with VocabularyData() as data:
            data.list(num=number, forgot=forgot)


if __name__ == "__main__":
    app()
