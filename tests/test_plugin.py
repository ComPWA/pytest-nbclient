from __future__ import annotations

from typing import TYPE_CHECKING

import nbformat
import pytest
import zmq

if TYPE_CHECKING:
    from pathlib import Path


def _write_notebook(path: Path, *sources: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cells = [nbformat.v4.new_code_cell(src) for src in sources]
    notebook = nbformat.v4.new_notebook(cells=cells)
    notebook.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nbformat.write(notebook, path)


def test_collection_is_opt_in(pytester: pytest.Pytester):
    _write_notebook(pytester.path / "docs" / "ok.ipynb", "x = 1")
    result = pytester.runpytest("docs")
    assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED


def test_passing_and_failing_notebooks(pytester: pytest.Pytester):
    _write_notebook(pytester.path / "docs" / "ok.ipynb", "x = 1", "assert x == 1")
    _write_notebook(pytester.path / "docs" / "bad.ipynb", "1 / 0")
    result = pytester.runpytest("--nbclient", "docs")
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines(["*ZeroDivisionError*"])


def test_runs_in_notebook_directory(pytester: pytest.Pytester):
    (pytester.path / "docs" / "sub").mkdir(parents=True)
    (pytester.path / "docs" / "sub" / "data.txt").write_text("42")
    _write_notebook(
        pytester.path / "docs" / "sub" / "read.ipynb",
        "assert open('data.txt').read() == '42'",
    )
    result = pytester.runpytest("--nbclient", "docs")
    result.assert_outcomes(passed=1)


def test_respects_ignore_and_norecursedirs(pytester: pytest.Pytester):
    pytester.makeini("[pytest]\nnorecursedirs = _build .*\n")
    _write_notebook(pytester.path / "docs" / "ok.ipynb", "x = 1")
    _write_notebook(pytester.path / "docs" / "skip.ipynb", "1 / 0")
    _write_notebook(pytester.path / "docs" / "_build" / "copy.ipynb", "1 / 0")
    _write_notebook(pytester.path / "docs" / ".ipynb_checkpoints" / "ok.ipynb", "1 / 0")
    result = pytester.runpytest("--nbclient", "--ignore=docs/skip.ipynb", "docs")
    result.assert_outcomes(passed=1)


@pytest.mark.skipif(not zmq.has("ipc"), reason="IPC transport is not supported")
@pytest.mark.parametrize(
    ("args", "warns"),
    [((), False), (("--nbclient-transport=tcp",), True)],
    ids=["default-ipc", "tcp"],
)
def test_ipc_transport_avoids_tcp_warning(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
    args: tuple[str, ...],
    warns: bool,
):
    monkeypatch.setenv("IPYTHONDIR", str(pytester.path / ".ipython"))
    _write_notebook(pytester.path / "docs" / "ok.ipynb", "x = 1")
    result = pytester.runpytest_subprocess("--nbclient", "-s", *args, "docs")
    result.assert_outcomes(passed=1)
    output = result.stdout.str() + result.stderr.str()
    assert ("Kernel is running over TCP without encryption" in output) is warns
    assert not list(pytester.path.glob("kernel-*"))
