# check-pyjson5

## Introduction

This is a pre-commit hook which verifies that `.json` and `.json5` files in a repository are valid [JSON5](https://json5.org/). The JSON5 format is similar to JSON, but it permits comments, trailing commas, and more. It is similar to the so-called "JSONC" (JSON with Comments) format, but JSON5 has an actual specification.

This hook is a drop-in replacement for the `check-json` hook from the [official pre-commit-hooks repository](https://pre-commit.com/hooks.html). A file succeeds when it can be parsed by the [pyjson5](https://pypi.org/project/pyjson5/) library, a fast JSON5 parser written in Cython. (In contrast, `check-json` uses the built-in [json library](https://docs.python.org/3/library/json.html).) Like `check-json`, the hook also rejects objects that contain duplicate keys. Keys are compared after decoding, so `"a"`, `'a'`, `a` and `"\u0061"` all count as the same key.

## Usage

In `.pre-commit-config.yaml` under the `repos:` section, add the following:

```yaml
- repo: https://github.com/lanshark/check-pyjson5
  rev: v1.0.2
  hooks:
    - id: check-pyjson5
```

(The original `check-json` hook should probably be removed in case it is already included.)

## Development

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11 or later.

```sh
uv sync
uv run pytest
uv run pre-commit install  # optional: run linters on each commit
```

## Credits

The actual code for this hook was written by [@asottile and various contributors to the official pre-commit-hooks repository](https://github.com/pre-commit/pre-commit-hooks/commits/master/pre_commit_hooks/check_json.py). A subsequent author (Ben Mares) replaced the `json` library with `json5` and published it as a separate hook. The current author (Scott Sharkey) replaced the `json5` library with the faster `pyjson5` library.

## License

This hook is published under the [MIT license](LICENSE). The original pre-commit-hooks collection (from which this hook is derived) is also published under the MIT license, [included here](LICENSE.pre-commit-hooks).
