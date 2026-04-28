from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi


OUTPUT_DIR = Path("Research") / "Youtube-Transcripts"


def extract_video_id(url: str) -> str:
    """Extract a YouTube video ID from common YouTube URL formats."""
    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if "youtu.be" in host:
        video_id = parsed.path.strip("/")
    elif "youtube.com" in host:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith("/shorts/") or parsed.path.startswith("/embed/"):
            video_id = parsed.path.strip("/").split("/")[1]
        else:
            video_id = ""
    else:
        video_id = ""

    if not re.fullmatch(r"[\w-]{11}", video_id):
        raise ValueError("Could not extract a valid YouTube video ID from the URL.")

    return video_id


def build_output_path(video_id: str) -> Path:
    return OUTPUT_DIR / f"{video_id}.txt"


def fetch_transcript_text(video_id: str) -> str:
    transcript = YouTubeTranscriptApi().fetch(video_id)
    return "\n".join(entry.text for entry in transcript)


def save_transcript(url: str) -> Path:
    video_id = extract_video_id(url)
    transcript_text = fetch_transcript_text(video_id)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = build_output_path(video_id)
    output_path.write_text(transcript_text, encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a YouTube transcript and save it as a text file."
    )
    parser.add_argument("url", help="The YouTube video URL.")
    args = parser.parse_args()

    output_path = save_transcript(args.url)
    print(f"Transcript saved to: {output_path}")


if __name__ == "__main__":
    main()
