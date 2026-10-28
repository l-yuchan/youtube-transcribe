#!/usr/bin/env python3
"""
YouTube Transcript Fetcher CLI

Fetches transcripts from YouTube videos and outputs to stdout.

Usage:
    yt-transcribe URL [--format FORMAT]
    echo "URL" | yt-transcribe
"""

import sys
import io
import re
import argparse
import json
from importlib.metadata import PackageNotFoundError, version
from urllib.parse import parse_qs, urlsplit

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url_or_id: str) -> str:
    """Extract a complete video ID from an ID or a supported YouTube URL."""
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", url_or_id):
        return url_or_id

    url = urlsplit(url_or_id if "://" in url_or_id else f"https://{url_or_id}")
    video_id = ""
    if url.scheme in {"http", "https"}:
        host = url.netloc.lower()
        if host in {"youtu.be", "www.youtu.be"}:
            video_id = url.path.removeprefix("/")
        elif host in {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}:
            if url.path == "/watch":
                values = parse_qs(url.query, keep_blank_values=True).get("v", [])
                if len(values) == 1:
                    video_id = values[0]
            else:
                parts = url.path.split("/")
                if len(parts) == 3 and parts[1] in {"embed", "shorts", "live"}:
                    video_id = parts[2]

    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", video_id):
        return video_id
    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS or HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def configure_stdio() -> None:
    """Write UTF-8 instead of the platform ANSI code page."""
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8")


def cli_version() -> str:
    """Return the installed distribution version, or a source-checkout label."""
    try:
        return version("youtube-transcribe")
    except PackageNotFoundError:
        return "unreleased"


def main() -> None:
    configure_stdio()
    parser = argparse.ArgumentParser(
        prog="yt-transcribe",
        description="Fetch YouTube video transcripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  yt-transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
  yt-transcribe VIDEO_ID --format timestamp
  echo "https://youtu.be/VIDEO_ID" | yt-transcribe
        """,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {cli_version()}",
        help="Show the installed version and exit",
    )
    parser.add_argument("url", nargs="?", help="YouTube URL or video ID")
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "timestamp"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--lang", "-l",
        default="en",
        help="Language code (default: en)",
    )

    args = parser.parse_args()

    # Get URL from argument or stdin
    url = args.url
    if not url and not sys.stdin.isatty():
        url = sys.stdin.read().strip()

    if not url:
        parser.print_help()
        sys.exit(1)

    try:
        video_id = extract_video_id(url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id, languages=[args.lang])

        if args.format == "json":
            print(json.dumps(transcript.to_raw_data(), indent=2))
        elif args.format == "timestamp":
            for snippet in transcript:
                ts = format_timestamp(snippet.start)
                print(f"[{ts}] {snippet.text}")
        else:
            print(" ".join(snippet.text for snippet in transcript))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
