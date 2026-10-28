# YouTube Transcribe

A simple CLI tool to fetch transcripts from YouTube videos.

> Fork of [shawn-dsz/youtube-transcribe](https://github.com/shawn-dsz/youtube-transcribe),
> packaged with uv and installable as a global `yt-transcribe` command.

## Features

- Fetch transcripts from any YouTube video with available captions
- Multiple output formats: plain text, timestamps, or JSON
- Support for different languages
- Accepts watch, short-link, Shorts, embed, and live URLs or an 11-character video ID
- Pipe-friendly: reads from stdin when no URL argument is provided

## Installation

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first.
Python 3.14 or newer is required; uv downloads it automatically when missing.

### Global install

```bash
uv tool install "git+https://github.com/l-yuchan/youtube-transcribe.git"
yt-transcribe --help
```

From a local clone, install the checkout instead:

```bash
git clone https://github.com/l-yuchan/youtube-transcribe.git
cd youtube-transcribe
uv tool install .
```

Reinstall a path install after changing the code with `uv tool install --force .`,
refresh a git install with `uv tool upgrade youtube-transcribe`, and remove the
command with `uv tool uninstall youtube-transcribe`.
`uv tool install` puts `yt-transcribe` on your PATH in its own isolated environment,
so it works from any directory on Windows, macOS, and Linux without activating a
virtual environment.

### Run without installing

```bash
uvx --from git+https://github.com/l-yuchan/youtube-transcribe.git yt-transcribe VIDEO_ID
```

## Usage

```bash
# Basic usage - get transcript as plain text
yt-transcribe "https://www.youtube.com/watch?v=VIDEO_ID"

# Using just the video ID
yt-transcribe VIDEO_ID

# With timestamps
yt-transcribe VIDEO_ID --format timestamp

# Full JSON output with timing data
yt-transcribe VIDEO_ID --format json

# Different language (e.g., German)
yt-transcribe VIDEO_ID --lang de

# Pipe from stdin
echo "https://youtu.be/VIDEO_ID" | yt-transcribe
```

`VIDEO_ID` is a placeholder; replace it with an actual 11-character video ID.
Inside a checkout, `uv run --locked yt-transcribe ...` runs the same command from
the locked project environment instead of the installed tool.

YouTube must provide captions in the requested language. Missing captions or
YouTube network/IP restrictions produce an error on stderr and a nonzero exit.

## Output Formats

### Text (default)
Plain text with all transcript segments joined together:
```
Hello everyone welcome to this video today we're going to talk about...
```

### Timestamp
Each line prefixed with the timestamp:
```
[0:00] Hello everyone
[0:03] welcome to this video
[0:05] today we're going to talk about...
```

### JSON
Full structured data with start time and duration for each segment:
```json
[
  {
    "text": "Hello everyone",
    "start": 0.0,
    "duration": 2.5
  },
  ...
]
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--format` | `-f` | Output format: `text`, `timestamp`, or `json` (default: `text`) |
| `--lang` | `-l` | Language code for transcript (default: `en`) |

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Python 3.14+
- Dependencies are declared in `pyproject.toml` and locked in `uv.lock`.

## Development

```bash
uv sync --locked
uv run --locked pytest
uv run --locked yt-transcribe VIDEO_ID
uv build
```

Development dependencies, including pytest, are installed by `uv sync`.
After changing dependencies in `pyproject.toml`, run `uv lock` and include
the updated `uv.lock` with the change.
The CLI is a normal installed command, so `uvx --from <repo or path> yt-transcribe`
checks packaging without touching your global tool environment.

## License

MIT License - see [LICENSE](LICENSE) for details.
