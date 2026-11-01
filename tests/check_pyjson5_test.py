import pytest

from pre_commit_hooks.check_pyjson5 import main
from pre_commit_hooks.check_pyjson5 import raise_duplicate_keys


@pytest.mark.parametrize(
    'content',
    (
        '{"a": 1, "b": [1, 2, 3]}',
        '// comment\n{\n  a: 1, /* block */ b: "x",\n}\n',
        "{'single': 'quotes', trailing: [1, 2,],}",
        '{hex: 0x1F, inf: -Infinity, nan: NaN, lead: .5, plus: +1}',
        '[{"a": 1}, {"a": 2}]',
        '{"a": {"a": {"a": 1}}}',
        '{"x": "{\\"a\\": 1, \\"a\\": 2}"}',
        '{"x": "a // not a comment", y: \'/* nor this */\'}',
        '"just a string"',
        '42',
        '﻿{"bom": true}',
        '{"a\\nb": 1, "a\\\\nb": 2}',
    ),
)
def test_valid(tmp_path, content):
    f = tmp_path / 'f.json'
    f.write_text(content, encoding='utf-8')
    assert main([str(f)]) == 0


@pytest.mark.parametrize(
    'content',
    (
        '{bad',
        '{"a": 1',
        '{"a": }',
        '[1, 2',
        '{"a": undefined}',
        '',
    ),
)
def test_invalid(tmp_path, capsys, content):
    f = tmp_path / 'f.json'
    f.write_text(content, encoding='utf-8')
    assert main([str(f)]) == 1
    assert f'{f}: Failed to json decode' in capsys.readouterr().out


def test_invalid_message_is_clean(tmp_path, capsys):
    f = tmp_path / 'f.json'
    f.write_text('{bad', encoding='utf-8')
    assert main([str(f)]) == 1
    assert capsys.readouterr().out == (
        f"{f}: Failed to json decode (Unclosed b'object' starting near 1)\n"
    )


def test_invalid_utf8(tmp_path, capsys):
    f = tmp_path / 'f.json'
    f.write_bytes(b'{"a": "\xff"}')
    assert main([str(f)]) == 1
    assert 'Failed to json decode' in capsys.readouterr().out


@pytest.mark.parametrize(
    'content',
    (
        '{"a": 1, "a": 2}',
        "{a: 1, 'a': 2}",
        '{"a": 1, \\u0061: 2}',
        '{"\\u0061": 1, "a": 2}',
        '{"outer": {"x": 1, /* , */ "x": 2}}',
        '[{"ok": 1}, {"b": 1, // c\n b: 2}]',
        '{"a": [1, {"k": 1}], "a": 2}',
    ),
)
def test_duplicate_keys(tmp_path, capsys, content):
    f = tmp_path / 'f.json'
    f.write_text(content, encoding='utf-8')
    assert main([str(f)]) == 1
    assert 'Duplicate key' in capsys.readouterr().out


def test_raise_duplicate_keys_message():
    with pytest.raises(ValueError, match="Duplicate key: 'a'"):
        raise_duplicate_keys('{"a": 1, "a": 2}')


def test_continues_after_bad_file(tmp_path, capsys):
    bad = tmp_path / 'bad.json'
    bad.write_text('{bad', encoding='utf-8')
    dup = tmp_path / 'dup.json'
    dup.write_text('{"a": 1, "a": 2}', encoding='utf-8')
    good = tmp_path / 'good.json'
    good.write_text('{"a": 1}', encoding='utf-8')

    assert main([str(bad), str(good), str(dup)]) == 1
    out = capsys.readouterr().out
    assert str(bad) in out
    assert str(dup) in out
    assert str(good) not in out
