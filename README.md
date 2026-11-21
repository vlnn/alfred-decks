# Decks workflow for Alfred

A thin front end for the `decks` command. The workflow passes arguments and shows results; it holds no deck logic.

## Files

- `info.plist`: the workflow definition.
- `filter.sh`: lists the actions for the `decks` keyword.
- `run.sh`: runs the chosen action and decides how to show the result.
- `package.sh`: builds `Decks.alfredworkflow`.
- `tests/`: `uv run --with pytest pytest`.

## What it expects from `decks`

- `decks sync|build|rebuild|status --dir DIR`, `decks sync --force --dir DIR` and `decks add --dir DIR -- TEXT`.
- Exit status 0 on success and non-zero on any failure, including "already running".
- On success, the last line of output is a one-line summary; it becomes the notification.
- The log is written to `DIR/toanki/decks.log`.

## How results are shown

| Result | Shown as |
|---|---|
| success | notification with the summary line |
| `status` | text view |
| failure of up to 6 lines | Large Type |
| longer failure | text view |
| rejected card | Large Type, and the text is copied to the clipboard |

## Configuration

Set in Alfred's workflow configuration: the decks directory (default `~/decks`) and the path to the `decks` executable (default `~/.local/bin/decks`).

## CI and releases

GitHub Actions runs on every push to `main` and on pull requests:

- the tests on Linux and on macOS, where `/bin/bash` is the same old bash that Alfred uses;
- `plutil -lint` on `info.plist`;
- a build of `Decks.alfredworkflow`, kept as a downloadable artifact of the run.

To publish a release, push a tag such as `v0.2.0`. The workflow's version is set from the tag and `Decks.alfredworkflow` is attached to a GitHub release with generated notes.
