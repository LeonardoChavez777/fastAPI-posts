from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from imageio_ffmpeg import get_ffmpeg_exe

router = APIRouter(prefix="/audio", tags=["Audio"])

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".mp4", ".m4a"}
MEDIA_TYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "mp4": "audio/mp4",
    "m4a": "audio/mp4",
}

FFMPEG_BIN = Path(get_ffmpeg_exe())
AUDIO_HISTORY_DIR = Path(__file__).resolve().parents[2] / "audio_history"
AUDIO_HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _run_ffmpeg(command: List[str], cwd: Path | None = None) -> None:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "Audio processing failed"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

def _build_html_interface() -> str:
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Combinar audios en loop</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f7f7fb;
            margin: 0;
            padding: 32px;
            color: #1f2937;
        }
        .card {
            max-width: 760px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
        }
        h1 {
            margin-top: 0;
        }
        form {
            display: grid;
            gap: 16px;
        }
        label {
            font-weight: 600;
        }
        input, select, button {
            font-size: 16px;
            padding: 10px 12px;
            border-radius: 10px;
            border: 1px solid #cbd5e1;
        }
        button {
            cursor: pointer;
            background: #2563eb;
            color: white;
            border: none;
            font-weight: 700;
        }
        .status {
            margin-top: 14px;
            font-weight: 600;
            color: #0f766e;
        }
        .hint {
            color: #475569;
            font-size: 14px;
        }
        .history-section {
            margin-top: 24px;
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
        }
        .history-item {
            margin-top: 12px;
            padding: 12px;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            background: #f8fafc;
        }
        .history-item p {
            margin: 0 0 8px 0;
            font-weight: 700;
        }
        .history-actions {
            display: flex;
            justify-content: flex-end;
            margin-top: 16px;
        }
        .danger-button {
            background: #dc2626;
            color: white;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Combinar audios y ponerlos en loop</h1>
        <p class="hint">Sube varios archivos en formato MP3, WAV o MP4. El endpoint los combina en un solo audio y lo repite el número de veces que indiques.</p>
        <form id="audio-form" enctype="multipart/form-data">
            <label for="files">Audios a combinar</label>
            <input id="files" name="files" type="file" multiple accept=".mp3,.wav,.mp4,.m4a,audio/mpeg,audio/wav,audio/mp4" required />

            <label for="loop_count">Número de repeticiones</label>
            <input id="loop_count" name="loop_count" type="number" min="1" max="20" value="3" required />

            <label for="output_format">Formato de salida</label>
            <select id="output_format" name="output_format">
                <option value="wav">WAV</option>
                <option value="mp3">MP3</option>
                <option value="mp4">MP4</option>
                <option value="m4a">M4A</option>
            </select>

            <button type="submit">Combinar audio</button>
        </form>
        <div id="status" class="status" aria-live="polite"></div>

        <section class="history-section">
            <h2>Audios combinados anteriores</h2>
            <div class="history-actions">
                <button id="clear-history-button" class="danger-button" type="button">Limpiar audios anteriores</button>
            </div>
            <div id="history-list"></div>
        </section>
    </div>
    <script>
        const form = document.getElementById('audio-form');
        const status = document.getElementById('status');
        const historyList = document.getElementById('history-list');
        const clearHistoryButton = document.getElementById('clear-history-button');

        async function refreshHistory() {
            try {
                const response = await fetch('/audio/history');
                const data = await response.json();
                historyList.innerHTML = '';

                if (!data.items.length) {
                    historyList.innerHTML = '<p class="hint">Todavía no hay audios combinados guardados.</p>';
                    return;
                }

                data.items.forEach((item) => {
                    const wrapper = document.createElement('div');
                    wrapper.className = 'history-item';

                    const label = document.createElement('p');
                    label.textContent = item.name;

                    const audio = document.createElement('audio');
                    audio.controls = true;
                    audio.src = item.url;
                    audio.style.width = '100%';

                    wrapper.appendChild(label);
                    wrapper.appendChild(audio);
                    historyList.appendChild(wrapper);
                });
            } catch (error) {
                console.error(error);
                historyList.innerHTML = '<p class="hint">No se pudo cargar el historial de audio.</p>';
            }
        }

        clearHistoryButton.addEventListener('click', async () => {
            const confirmed = window.confirm('¿Seguro que quieres borrar todos los audios combinados anteriores?');
            if (!confirmed) {
                return;
            }

            status.textContent = 'Limpiando historial...';
            try {
                const response = await fetch('/audio/history', {
                    method: 'DELETE',
                });

                if (!response.ok) {
                    const error = await response.json().catch(() => ({ detail: 'No se pudo limpiar el historial.' }));
                    status.textContent = error.detail || 'No se pudo limpiar el historial.';
                    return;
                }

                await refreshHistory();
                status.textContent = 'Historial limpiado correctamente.';
            } catch (error) {
                status.textContent = 'Ocurrió un error al limpiar el historial.';
                console.error(error);
            }
        });

        window.addEventListener('DOMContentLoaded', refreshHistory);

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const files = document.getElementById('files').files;

            if (!files.length) {
                status.textContent = 'Debes seleccionar al menos un archivo.';
                return;
            }

            status.textContent = 'Procesando audio...';
            const formData = new FormData(form);

            try {
                const response = await fetch('/audio/combine-loop', {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    const error = await response.json().catch(() => ({ detail: 'No se pudo generar la mezcla.' }));
                    status.textContent = error.detail || 'No se pudo generar la mezcla.';
                    return;
                }

                const blob = await response.blob();
                const outputFormat = document.getElementById('output_format').value;
                const audioUrl = URL.createObjectURL(blob);
                const audio = document.createElement('audio');
                audio.controls = true;
                audio.src = audioUrl;
                audio.style.width = '100%';
                audio.style.marginTop = '16px';

                const existingPlayer = document.getElementById('audio-player');
                if (existingPlayer) {
                    existingPlayer.remove();
                }

                audio.id = 'audio-player';
                document.querySelector('.card').appendChild(audio);

                const downloadUrl = URL.createObjectURL(blob);
                const anchor = document.createElement('a');
                anchor.href = downloadUrl;
                anchor.download = `looped-audio.${outputFormat}`;
                anchor.textContent = 'Descargar archivo generado';
                anchor.style.display = 'inline-block';
                anchor.style.marginTop = '12px';
                anchor.style.color = '#2563eb';

                const existingDownloadLink = document.getElementById('download-link');
                if (existingDownloadLink) {
                    existingDownloadLink.remove();
                }

                anchor.id = 'download-link';
                document.querySelector('.card').appendChild(anchor);
                await refreshHistory();
                status.textContent = '¡Audio combinado y listo para reproducir!';
            } catch (error) {
                status.textContent = 'Ocurrió un error al procesar el archivo.';
                console.error(error);
            }
        });
    </script>
</body>
</html>
"""


@router.get("/interface", response_class=HTMLResponse)
def audio_interface():
    return HTMLResponse(content=_build_html_interface())


@router.get("/history")
def audio_history():
    items = []
    for audio_path in sorted(AUDIO_HISTORY_DIR.glob("*"), key=lambda path: path.stat().st_mtime, reverse=True):
        if audio_path.is_file() and audio_path.suffix.lower().lstrip(".") in MEDIA_TYPES:
            items.append(
                {
                    "name": audio_path.name,
                    "url": f"/audio/history-files/{audio_path.name}",
                }
            )

    return JSONResponse({"items": items})


@router.delete("/history")
def clear_audio_history():
    deleted_count = 0
    for audio_path in AUDIO_HISTORY_DIR.glob("*"):
        if audio_path.is_file():
            audio_path.unlink()
            deleted_count += 1

    return JSONResponse({"deleted": deleted_count})


@router.get("/history-files/{filename}")
def audio_history_file(filename: str):
    safe_name = Path(filename).name
    target_path = AUDIO_HISTORY_DIR / safe_name

    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio no encontrado.")

    return FileResponse(
        target_path,
        media_type=MEDIA_TYPES.get(target_path.suffix.lower().lstrip("."), "application/octet-stream"),
        headers={"Content-Disposition": f'inline; filename="{target_path.name}"'},
    )


@router.post("/combine-loop")
async def combine_loop(
    files: List[UploadFile] = File(...),
    loop_count: int = Form(1),
    output_format: str = Form("mp3"),
):
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debes enviar al menos un archivo.")

    if loop_count < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="loop_count debe ser mayor o igual a 1.")

    output_format = output_format.lower().strip()
    if output_format not in MEDIA_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de salida no soportado. Usa mp3, wav o mp4.")

    with tempfile.TemporaryDirectory(prefix="audio-loop-") as temp_dir:
        temp_path = Path(temp_dir)
        converted_files: List[Path] = []

        for index, uploaded_file in enumerate(files):
            if not uploaded_file.filename:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cada archivo debe tener un nombre válido.")

            file_extension = Path(uploaded_file.filename).suffix.lower()
            if file_extension not in SUPPORTED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Formato no soportado: {uploaded_file.filename}. Solo se aceptan mp3, wav, mp4 y m4a.",
                )

            source_path = temp_path / f"input_{index}_original{file_extension}"
            source_bytes = await uploaded_file.read()
            source_path.write_bytes(source_bytes)

            converted_path = temp_path / f"input_{index}_converted.wav"
            _run_ffmpeg(
                [
                    str(FFMPEG_BIN),
                    "-y",
                    "-i",
                    str(source_path),
                    "-vn",
                    "-acodec",
                    "pcm_s16le",
                    "-ar",
                    "44100",
                    str(converted_path),
                ]
            )
            converted_files.append(converted_path)

        concat_list_path = temp_path / "concat.txt"
        concat_content = "\n".join([f"file '{path.as_posix()}'" for path in converted_files]) + "\n"
        concat_list_path.write_text(concat_content, encoding="utf-8")

        combined_wav = temp_path / "combined.wav"
        _run_ffmpeg(
            [
                str(FFMPEG_BIN),
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_list_path),
                "-c:a",
                "pcm_s16le",
                str(combined_wav),
            ]
        )

        looped_audio = temp_path / "looped.wav"
        _run_ffmpeg(
            [
                str(FFMPEG_BIN),
                "-y",
                "-stream_loop",
                str(loop_count - 1),
                "-i",
                str(combined_wav),
                "-c:a",
                "pcm_s16le",
                str(looped_audio),
            ]
        )

        output_path = temp_path / f"looped_audio.{output_format}"
        if output_format == "wav":
            _run_ffmpeg([
                str(FFMPEG_BIN),
                "-y",
                "-i",
                str(looped_audio),
                "-c:a",
                "pcm_s16le",
                str(output_path),
            ])
        elif output_format == "mp3":
            _run_ffmpeg([
                str(FFMPEG_BIN),
                "-y",
                "-i",
                str(looped_audio),
                "-vn",
                "-codec:a",
                "libmp3lame",
                str(output_path),
            ])
        elif output_format == "m4a":
            _run_ffmpeg([
                str(FFMPEG_BIN),
                "-y",
                "-i",
                str(looped_audio),
                "-vn",
                "-codec:a",
                "aac",
                str(output_path),
            ])
        else:
            _run_ffmpeg([
                str(FFMPEG_BIN),
                "-y",
                "-i",
                str(looped_audio),
                "-vn",
                "-codec:a",
                "aac",
                str(output_path),
            ])

        download_filename = f"combined-loop_{uuid4().hex}.{output_format}"
        final_bytes = output_path.read_bytes()
        persisted_output_path = AUDIO_HISTORY_DIR / download_filename
        persisted_output_path.write_bytes(final_bytes)

    return Response(
        content=final_bytes,
        media_type=MEDIA_TYPES[output_format],
        headers={
            "Content-Disposition": f'inline; filename="{download_filename}"',
            "Content-Type": MEDIA_TYPES[output_format],
        },
    )
