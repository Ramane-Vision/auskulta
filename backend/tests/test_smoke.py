"""
Smoke test: upload one tiny generated video to /api/analyze and assert the
pipeline completes end-to-end with a 200. Not a correctness test (scores
aren't asserted) — just a safety net against import/wiring regressions.

Requires ffmpeg on PATH (used to generate the throwaway test clip).
"""

import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(scope="module")
def dummy_video():
    with NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        path = tmp.name
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=duration=1:size=160x120:rate=10",
            "-f", "lavfi", "-i", "sine=frequency=220:duration=1",
            "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p", path,
        ],
        check=True,
        capture_output=True,
    )
    yield path
    Path(path).unlink(missing_ok=True)


def test_analyze_returns_200(dummy_video):
    with open(dummy_video, "rb") as f:
        response = client.post("/api/analyze", files={"file": ("test.mp4", f, "video/mp4")})

    assert response.status_code == 200
    body = response.json()
    assert "visual" in body
    assert "risk_score" in body
    assert "reasoning" in body


def test_analyze_rejects_unsupported_extension():
    response = client.post("/api/analyze", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert response.status_code == 400
