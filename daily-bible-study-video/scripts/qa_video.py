#!/usr/bin/env python3
"""Basic technical QA for a rendered daily Bible-study video."""

import json
import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: qa_video.py <video.mp4>", file=sys.stderr)
        return 2
    video = Path(sys.argv[1]).resolve()
    if not video.is_file():
        print(f"missing video: {video}", file=sys.stderr)
        return 2

    probe = run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(video),
    ])
    if probe.returncode:
        print(probe.stderr, file=sys.stderr)
        return 1
    data = json.loads(probe.stdout)
    streams = data.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    checks = {
        "has_video": video_stream is not None,
        "has_audio": audio_stream is not None,
        "vertical_720x1280": bool(video_stream and video_stream.get("width") == 720 and video_stream.get("height") == 1280),
        "h264": bool(video_stream and video_stream.get("codec_name") == "h264"),
        "aac": bool(audio_stream and audio_stream.get("codec_name") == "aac"),
        "duration_seconds": float(data.get("format", {}).get("duration", 0)),
        "size_bytes": int(data.get("format", {}).get("size", 0)),
    }
    decode = run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"])
    checks["full_decode_ok"] = decode.returncode == 0 and not decode.stderr.strip()
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    required = ("has_video", "has_audio", "vertical_720x1280", "h264", "aac", "full_decode_ok")
    return 0 if all(checks[key] for key in required) else 1


if __name__ == "__main__":
    raise SystemExit(main())

