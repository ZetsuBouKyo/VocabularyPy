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
def new(vocabulary: str = Argument(...)):
    with VocabularyData() as data:
        data.new(vocabulary, state=VocabularyState.READ.value)


@app.command()
def random(number: int = Option(10, "-n/"), forgot: bool = Option(False, "-f/")):
    with VocabularyData() as data:
        data.random(num=number, forgot=forgot)


@app.command()
def status():
    with VocabularyData() as data:
        data.status()


@app.command()
def today():
    with VocabularyData() as data:
        data.today()


@app.command()
def delete(vocabulary: List[str] = Option([], "-v/")):
    with VocabularyData() as data:
        for v in vocabulary:
            data.delete(v)


@app.command()
def list(
    forgot: bool = Option(False, "-f/"),
    number: int = Option(10, "-n/"),
    le: int = Option(None, "-le/"),
    vocabulary: str = Option(None, "-v/"),
):
    if vocabulary is not None:
        with VocabularyData() as data:
            data.info(vocabulary)
    else:
        with VocabularyData() as data:
            data.list(num=number, forgot=forgot, le=le)


if __name__ == "__main__":
    app()
