from pathlib import Path

import pytest

from app.routers import audio as audio_router


@pytest.fixture(autouse=True)
def isolated_audio_history(tmp_path, monkeypatch):
    history_dir = tmp_path / "audio_history"
    history_dir.mkdir()
    monkeypatch.setattr(audio_router, "AUDIO_HISTORY_DIR", history_dir)
    yield history_dir


def test_audio_interface(client):
    response = client.get("/audio/interface")

    assert response.status_code == 200
    assert "Combinar audios" in response.text


def test_audio_history_empty(client):
    response = client.get("/audio/history")

    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_clear_audio_history(client, isolated_audio_history):
    sample_file = isolated_audio_history / "sample.wav"
    sample_file.write_bytes(b"fake-audio")

    response = client.delete("/audio/history")

    assert response.status_code == 200
    assert response.json()["deleted"] == 1
    assert not any(Path(isolated_audio_history).iterdir())


def test_combine_loop_requires_files(client):
    response = client.post("/audio/combine-loop", data={"loop_count": "1", "output_format": "wav"})

    assert response.status_code == 422
