from pathlib import Path

import pytest

from scripts.frontend.sync_frontend_data import FILES, sync_frontend_data


def test_sync_frontend_data_copies_required_files_without_changes(tmp_path):
    source_dir = tmp_path / "outputs" / "predictions"
    frontend_dir = tmp_path / "frontend"
    source_dir.mkdir(parents=True)
    frontend_dir.mkdir()

    for filename in FILES:
        (source_dir / filename).write_text(f'{{"file": "{filename}"}}', encoding="utf-8")

    assert sync_frontend_data(source_dir, frontend_dir) is True

    for filename in FILES:
        assert (frontend_dir / "public" / "data" / filename).read_bytes() == (
            source_dir / filename
        ).read_bytes()


def test_sync_frontend_data_skips_missing_frontend(tmp_path, capsys):
    source_dir = tmp_path / "outputs" / "predictions"

    assert sync_frontend_data(source_dir, tmp_path / "missing-frontend") is False
    assert "Warning: frontend directory not found" in capsys.readouterr().out


def test_sync_frontend_data_fails_when_a_required_source_is_missing(tmp_path):
    source_dir = tmp_path / "outputs" / "predictions"
    frontend_dir = tmp_path / "frontend"
    source_dir.mkdir(parents=True)
    frontend_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="Missing required prediction files"):
        sync_frontend_data(source_dir, frontend_dir)


def test_sync_frontend_data_copies_optional_files_when_present(tmp_path):
    from scripts.frontend.sync_frontend_data import OPTIONAL_FILES

    source_dir = tmp_path / "outputs" / "predictions"
    frontend_dir = tmp_path / "frontend"
    source_dir.mkdir(parents=True)
    frontend_dir.mkdir()
    for filename in FILES:
        (source_dir / filename).write_text("{}", encoding="utf-8")
    (source_dir / OPTIONAL_FILES[0]).write_text('{"optional": true}', encoding="utf-8")

    sync_frontend_data(source_dir, frontend_dir)

    destination = frontend_dir / "public" / "data"
    assert (destination / OPTIONAL_FILES[0]).read_text(encoding="utf-8") == '{"optional": true}'
    assert not (destination / OPTIONAL_FILES[1]).exists()
