import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from youtube_transcript_api import (
    FetchedTranscript,
    FetchedTranscriptSnippet,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

import yt_transcript


@pytest.mark.parametrize(
    "value",
    [
        "dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?feature=share&v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ?t=30",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://www.youtube.com/live/dQw4w9WgXcQ",
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        "http://youtube.com/watch?v=dQw4w9WgXcQ",
        "youtube.com/watch?v=dQw4w9WgXcQ",
        "https://WWW.YOUTUBE.COM/watch?v=dQw4w9WgXcQ",
    ],
)
def test_extracts_supported_video_url(value: str) -> None:
    # Given a supported URL or bare ID.
    # When it is parsed.
    result = yt_transcript.extract_video_id(value)
    # Then the entire video ID is returned.
    assert result == "dQw4w9WgXcQ"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "invalid",
        "https://notyoutube.com/watch?v=dQw4w9WgXcQ",
        "https://youtube.com.evil.example/watch?v=dQw4w9WgXcQ",
        "https://evil.example/youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtube.com@evil.example/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQEXTRA",
        "https://youtube.com/watch?v=dQw4w9WgXcQEXTRA",
        "https://youtu.be/dQw4w9WgXcQ/extra",
        "https://youtube.com/watch?v=",
        "https://youtube.com/watch?v=dQw4w9WgXcQ&v=abcdefghijk",
        "ftp://youtube.com/watch?v=dQw4w9WgXcQ",
    ],
)
def test_rejects_invalid_video_url(value: str) -> None:
    # Given an unsupported host, scheme, path or ID.
    # When it is parsed, then no partial ID is accepted.
    with pytest.raises(ValueError):
        yt_transcript.extract_video_id(value)


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [(0, "0:00"), (59.9, "0:59"), (60, "1:00"), (3599, "59:59"), (3600, "1:00:00")],
)
def test_formats_timestamp_boundary(seconds: float, expected: str) -> None:
    # Given a timestamp at a display boundary.
    # When it is formatted.
    result = yt_transcript.format_timestamp(seconds)
    # Then minutes and hours are displayed correctly.
    assert result == expected


@pytest.mark.parametrize("output_format", ["text", "timestamp", "json"])
def test_cli_formats_transcript_from_stdin(
    output_format: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Given real transcript objects and a deterministic external fetch boundary.
    transcript = FetchedTranscript(
        snippets=[
            FetchedTranscriptSnippet(text="Hello", start=0.0, duration=2.5),
            FetchedTranscriptSnippet(text="세계", start=3601.0, duration=1.5),
        ],
        video_id="dQw4w9WgXcQ",
        language="Korean",
        language_code="ko",
        is_generated=False,
    )

    def fetch(
        self: YouTubeTranscriptApi, video_id: str, languages: list[str]
    ) -> FetchedTranscript:
        assert video_id == "dQw4w9WgXcQ"
        assert languages == ["ko"]
        return transcript

    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", fetch)
    monkeypatch.setattr(sys, "argv", ["yt-transcribe", "-f", output_format, "-l", "ko"])
    monkeypatch.setattr(sys, "stdin", io.StringIO("https://youtu.be/dQw4w9WgXcQ\n"))
    # When the CLI consumes stdin.
    yt_transcript.main()
    # Then the selected output retains text and timing data.
    output = capsys.readouterr()
    assert output.err == ""
    if output_format == "json":
        assert json.loads(output.out) == [
            {"text": "Hello", "start": 0.0, "duration": 2.5},
            {"text": "세계", "start": 3601.0, "duration": 1.5},
        ]
    else:
        expected = (
            "Hello 세계\n"
            if output_format == "text"
            else "[0:00] Hello\n[1:00:01] 세계\n"
        )
        assert output.out == expected


def test_cli_writes_utf8_when_stdout_uses_a_legacy_code_page() -> None:
    # Given a legacy ANSI stdout encoding, as on Windows pipes and files.
    script = (
        "import yt_transcript;"
        "yt_transcript.configure_stdio();"
        "print('\\u266a')"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        cwd=Path(__file__).resolve().parent.parent,
        env={**os.environ, "PYTHONIOENCODING": "cp949"},
        check=False,
    )
    # Then non-ASCII text is emitted as UTF-8 rather than cp949.
    assert result.returncode == 0
    assert result.stdout.rstrip(b"\r\n") == "\u266a".encode()


def test_cli_reports_installed_version(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Given a request for the CLI version.
    monkeypatch.setattr(sys, "argv", ["yt-transcribe", "--version"])
    # When the CLI starts.
    with pytest.raises(SystemExit) as error:
        yt_transcript.main()
    # Then it exits successfully and prints the command with a version.
    assert error.value.code == 0
    program, reported = capsys.readouterr().out.strip().split(" ", 1)
    assert program == "yt-transcribe"
    assert reported


def test_cli_reports_disabled_transcript(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Given a known external service error.
    def fetch(
        self: YouTubeTranscriptApi, video_id: str, languages: list[str]
    ) -> FetchedTranscript:
        raise TranscriptsDisabled(video_id)

    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", fetch)
    monkeypatch.setattr(sys, "argv", ["yt-transcribe", "dQw4w9WgXcQ"])
    # When the CLI fetches unavailable captions.
    with pytest.raises(SystemExit) as error:
        yt_transcript.main()
    # Then it exits unsuccessfully without polluting stdout.
    assert error.value.code == 1
    assert capsys.readouterr().out == ""
