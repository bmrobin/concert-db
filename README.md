# concert DB
A TUI for tracking concerts you attend in your terminal.

Built with [Textual](https://textual.textualize.io/) & [SQLAlchemy](https://www.sqlalchemy.org/).

![Screenshot](/screenshot.png?raw=true)

## Requirements
* `task` - https://taskfile.dev/
  * `brew install go-task`
* `uv` - https://docs.astral.sh/uv/
  * `brew install uv`

## Installation
```sh
$ uv sync
$ source .venv/bin/activate
$ task all
```

### Scripts
_Use `task -l` to see all available tasks to run._

```sh
# launch app
task app

# test
task test

# lint
task lint

# run all checks
task all

# seed test data
task seed
```
