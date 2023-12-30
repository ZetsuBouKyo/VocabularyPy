import asyncio
import sys
from functools import wraps
from inspect import iscoroutinefunction
from typing import Optional

from typer import Typer


class CustomTyper(Typer):
    def __init__(
        self, *args, loop_factory: Optional[asyncio.AbstractEventLoop] = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.loop_factory = loop_factory

    def command(
        self,
        *args,
        airflow_dag_id: Optional[str] = None,
        airflow_dag_sub_command: Optional[str] = None,
        **kwargs
    ):
        decorator = super().command(*args, **kwargs)

        def add_runner(f):
            @wraps(f)
            def runner(*args, **kwargs):
                if sys.version_info >= (3, 11) and self.loop_factory:
                    with asyncio.Runner(loop_factory=self.loop_factory) as runner:
                        runner.run(f(*args, **kwargs))
                else:
                    asyncio.run(f(*args, **kwargs))

            if iscoroutinefunction(f):
                return decorator(runner)
            return decorator(f)

        return add_runner
