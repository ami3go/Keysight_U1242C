import pytest

from keysight_u1242c.cli import build_arg_parser, main


def test_cli_help(capsys):
    parser = build_arg_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    captured = capsys.readouterr()
    assert "u1242c-log" in captured.out


def test_cli_requires_port():
    with pytest.raises(SystemExit):
        main(["--once"])
