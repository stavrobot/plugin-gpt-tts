#!/usr/bin/env -S uv run
# /// script
# dependencies = ["requests"]
# ///

import json
import sys
from pathlib import Path

import requests


KNOWN_PARAMS = {"text", "instructions"}


def main() -> None:
    """Call the OpenAI TTS API and write the resulting MP3 to /tmp/gpt-audio/."""
    params = json.load(sys.stdin)
    unknown = set(params) - KNOWN_PARAMS
    if unknown:
        print(f"Unknown parameters: {', '.join(sorted(unknown))}", file=sys.stderr)
        sys.exit(1)

    if "text" not in params:
        print("Missing required parameter: text", file=sys.stderr)
        sys.exit(1)

    if not isinstance(params["text"], str):
        print("Parameter 'text' must be a string", file=sys.stderr)
        sys.exit(1)

    config = json.loads(Path("../config.json").read_text())
    api_key = config["api_key"]
    voice = config["voice"]

    request_body: dict[str, str] = {
        "model": "gpt-4o-mini-tts",
        "voice": voice,
        "input": params["text"],
        "response_format": "mp3",
    }
    if params.get("instructions"):
        request_body["instructions"] = params["instructions"]

    response = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=request_body,
    )

    if not response.ok:
        print(
            f"OpenAI TTS API error {response.status_code}: {response.text}",
            file=sys.stderr,
        )
        sys.exit(1)

    output_dir = Path("/tmp/gpt-audio")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "output.mp3").write_bytes(response.content)

    json.dump({"file": "output.mp3"}, sys.stdout)


main()
