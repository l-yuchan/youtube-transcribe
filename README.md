# YouTube Transcribe

A simple CLI tool to fetch transcripts from YouTube videos.

## Features

- Fetch transcripts from any YouTube video with available captions
- Multiple output formats: plain text, timestamps, or JSON
- Support for different languages
- Accepts YouTube URLs in various formats or just the video ID
- Pipe-friendly: reads from stdin when no URL argument is provided

## Installation

```bash
# Clone the repository
git clone https://github.com/shawn-dsz/youtube-transcribe.git
cd youtube-transcribe

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage - get transcript as plain text
./yt "https://www.youtube.com/watch?v=VIDEO_ID"

# Using just the video ID
./yt VIDEO_ID

# With timestamps
./yt VIDEO_ID --format timestamp

# Full JSON output with timing data
./yt VIDEO_ID --format json

# Different language (e.g., German)
./yt VIDEO_ID --lang de

# Pipe from stdin
echo "https://youtu.be/VIDEO_ID" | ./yt
```

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

- Python 3.7+
- `youtube-transcript-api` package

## License

MIT License - see [LICENSE](LICENSE) for details.
