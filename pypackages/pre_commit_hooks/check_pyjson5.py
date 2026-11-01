# Source: <https://github.com/pre-commit/pre-commit-hooks/blob/39ab2ed/pre_commit_hooks/check_json.py>  # noqa: E501
import argparse
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set

import pyjson5

_LINE_TERMINATORS = '\n\r  '
# Characters that end an unquoted token (identifier, number or literal).
_DELIMITERS = set('{}[]:,/"\'')


def _is_space(c: str) -> bool:
    return c.isspace() or c == '﻿'


def _decode_key(token: str) -> str:
    """Normalize a raw key token (quoted string or identifier, possibly
    containing escapes) by letting pyjson5 parse it."""
    return next(iter(pyjson5.decode(f'{{{token}:0}}')))


def raise_duplicate_keys(text: str) -> None:
    """Raise ``ValueError`` if any object in ``text`` repeats a key.

    pyjson5 has no ``object_pairs_hook``, so duplicates are found with a
    lightweight scan over the source. ``text`` must already be known to be
    valid JSON5; the scanner relies on that and does no validation itself.
    """
    # One entry per open container: a set of seen keys for objects,
    # None for arrays.
    stack: List[Optional[Set[str]]] = []
    expecting_key = False
    i, n = 0, len(text)

    while i < n:
        c = text[i]

        if _is_space(c):
            i += 1
            continue

        if c == '/' and text.startswith('//', i):
            i += 2
            while i < n and text[i] not in _LINE_TERMINATORS:
                i += 1
            continue

        if c == '/' and text.startswith('/*', i):
            end = text.find('*/', i + 2)
            i = n if end == -1 else end + 2
            continue

        if c == '{':
            stack.append(set())
            expecting_key = True
            i += 1
        elif c == '[':
            stack.append(None)
            expecting_key = False
            i += 1
        elif c in '}]':
            stack.pop()
            expecting_key = False
            i += 1
        elif c == ',':
            expecting_key = bool(stack) and stack[-1] is not None
            i += 1
        elif c == ':':
            expecting_key = False
            i += 1
        else:
            start = i
            if c in '"\'':
                i += 1
                while text[i] != c:
                    i += 2 if text[i] == '\\' else 1
                i += 1
            else:
                while (
                        i < n and
                        text[i] not in _DELIMITERS and
                        not _is_space(text[i])
                ):
                    i += 1
            if expecting_key:
                keys = stack[-1]
                assert keys is not None
                key = _decode_key(text[start:i])
                if key in keys:
                    raise ValueError(f'Duplicate key: {key!r}')
                keys.add(key)
                expecting_key = False


def check_file(filename: str) -> Optional[str]:
    """Return an error message for ``filename``, or None if it is valid."""
    with open(filename, 'rb') as f:
        data = f.read()
    try:
        text = data.decode('utf-8')
        pyjson5.decode(text)
        raise_duplicate_keys(text)
    except (pyjson5.Json5Exception, ValueError) as exc:
        return f'{filename}: Failed to json decode ({exc})'
    return None


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to check.')
    args = parser.parse_args(argv)

    retval = 0
    for filename in args.filenames:
        error = check_file(filename)
        if error is not None:
            print(error)
            retval = 1
    return retval


if __name__ == '__main__':
    raise SystemExit(main())
