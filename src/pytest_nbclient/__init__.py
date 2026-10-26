"""Execute Jupyter notebooks as pytest items with nbclient.

Collection is opt-in with :code:`--nbclient`, so that a plain :code:`pytest` run in a
repository with notebooks only runs its unit tests. Which notebooks are collected is
controlled with the usual pytest options, such as :code:`testpaths`,
:code:`norecursedirs`, and :code:`--ignore`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import nbformat
import pytest
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from _pytest._code.code import TerminalRepr, TracebackStyle


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("nbclient")
    group.addoption(
        "--nbclient",
        action="store_true",
        help="Execute *.ipynb files with nbclient.",
    )
    group.addoption(
        "--nbclient-timeout",
        default=None,
        type=int,
        help="Maximum seconds per cell; no limit by default.",
    )
    group.addoption(
        "--nbclient-kernel",
        default=None,
        help="Kernel name to use instead of the one in the notebook metadata.",
    )


def pytest_collect_file(
    parent: pytest.Collector, file_path: Path
) -> NotebookFile | None:
    if file_path.suffix == ".ipynb" and parent.config.getoption("nbclient"):
        return NotebookFile.from_parent(parent, path=file_path)
    return None


class NotebookFile(pytest.File):
    def collect(self) -> Iterator[NotebookItem]:
        yield NotebookItem.from_parent(self, name=self.path.name)


class NotebookItem(pytest.Item):
    def runtest(self) -> None:
        notebook = nbformat.read(self.path, as_version=nbformat.NO_CONVERT)
        kwargs = {}
        if kernel_name := self.config.getoption("nbclient_kernel"):
            kwargs["kernel_name"] = kernel_name
        client = NotebookClient(
            notebook,
            timeout=self.config.getoption("nbclient_timeout"),
            resources={"metadata": {"path": str(self.path.parent)}},
            **kwargs,
        )
        client.execute()

    def repr_failure(
        self,
        excinfo: pytest.ExceptionInfo[BaseException],
        style: TracebackStyle | None = None,
    ) -> str | TerminalRepr:
        if isinstance(excinfo.value, CellExecutionError):
            return str(excinfo.value)
        return super().repr_failure(excinfo, style=style)

    def reportinfo(self) -> tuple[Path, int, str]:
        return self.path, 0, str(self.path)
