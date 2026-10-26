# pytest-nbclient

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
A minimal [pytest](https://pytest.org) plugin that executes Jupyter notebooks with [nbclient](https://nbclient.readthedocs.io), as a lightweight replacement for [nbmake](https://github.com/treebeardtech/nbmake).

```shell
pytest --nbclient docs
```

Each notebook becomes one test item that passes when all of its cells execute without an error. Notebooks run from their own directory with the kernel named in their metadata, and there is no timeout unless you set `--nbclient-timeout`. Output is not compared against the stored output.

The kernel communicates over IPC sockets wherever the platform supports them, which avoids the warning that recent `ipykernel` versions emit about unencrypted TCP connections. Pass `--nbclient-transport=tcp` to use TCP instead.

Collection is opt-in through `--nbclient`, so a plain `pytest` run only collects your usual tests. Select or skip notebooks with standard pytest configuration, such as `testpaths`, `norecursedirs` (for instance `_build` and `.ipynb_checkpoints`), `--ignore`, and `-k`.

## Development

Use `uv sync` to prepare the development environment, or allow direnv to activate it through `.envrc`. Run `poe test` for the test suite and `poe style` for formatting, linting, and type checks. Run `poe upgrade` to refresh hook revisions and the dependency lock file. The configuration is maintained by [ComPWA/policy](https://github.com/ComPWA/policy).
