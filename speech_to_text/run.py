#!/usr/bin/env -S uv run
# /// script
# dependencies = ["av", "requests"]
# ///

import json
import sys
from pathlib import Path

import av
import requests


KNOWN_PARAMS = {"audio"}

SUPPORTED_EXTENSIONS = {".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"}

CONVERTED_PATH = Path("/tmp/gpt-audio/converted.wav")


def convert_to_wav(input_path: Path, output_path: Path) -> None:
    """Convert an audio file to WAV using PyAV.

    PyAV bundles its own FFmpeg libraries, so no system FFmpeg is required.
    We decode all audio frames from the input and re-encode them as 16-bit
    PCM WAV, preserving the original sample rate and channel layout without
    any resampling.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    input_container = av.open(str(input_path))
    output_container = av.open(str(output_path), mode="w", format="wav")
    input_stream = input_container.streams.audio[0]
    output_stream = output_container.add_stream("pcm_s16le", rate=input_stream.rate)
    output_stream.layout = input_stream.layout
    for frame in input_container.decode(audio=0):
        for packet in output_stream.encode(frame):
            output_container.mux(packet)
    for packet in output_stream.encode():
        output_container.mux(packet)
    output_container.close()
    input_container.close()


def main() -> None:
    """Call the OpenAI transcription API and return the transcribed text."""
    params = json.load(sys.stdin)
    unknown = set(params) - KNOWN_PARAMS
    if unknown:
        print(f"Unknown parameters: {', '.join(sorted(unknown))}", file=sys.stderr)
        sys.exit(1)

    if "audio" not in params:
        print("Missing required parameter: audio", file=sys.stderr)
        sys.exit(1)

    audio_path = Path(params["audio"])
    if audio_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        convert_to_wav(audio_path, CONVERTED_PATH)
        audio_path = CONVERTED_PATH

    config = json.loads(Path("../config.json").read_text())
    api_key = config["api_key"]
    stt_model = config.get("stt_model", "gpt-4o-transcribe")

    with open(audio_path, "rb") as audio_file:
        response = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": audio_file},
            data={"model": stt_model},
        )

    if not response.ok:
        print(
            f"OpenAI STT API error {response.status_code}: {response.text}",
            file=sys.stderr,
        )
        sys.exit(1)

    json.dump({"text": response.json()["text"]}, sys.stdout)


main()
