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

## Running
Run the app in one of two modes: `development` or `production`. This distinction is mostly just useful for having an
environment to test and work with while coding with a separate, dedicated SQLite database (see the `seed` task).

```sh
task prd

task dev
```

### Scripts
_Use `task -l` to see all available tasks to run._

```sh
# test
task test

# lint
task lint

# run all checks
task all

# seed test data
task seed
```
