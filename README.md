# gpt-audio

Text-to-speech and speech-to-text using OpenAI's audio APIs.

## Tools

- **text_to_speech** — converts text to an MP3 audio file.
- **speech_to_text** — transcribes an audio file to text.

## Installation

Ask the bot to install the plugin from `https://github.com/stavrobot/plugin-gpt-audio`.

## Configuration

After installation, set the following configuration values:

| Key | Required | Description |
|-----|----------|-------------|
| `api_key` | Yes | Your OpenAI API key. |
| `voice` | Yes | TTS voice to use. |
| `stt_model` | No | STT model (defaults to `gpt-4o-transcribe`). |

Available TTS voices: `alloy`, `ash`, `ballad`, `coral`, `echo`, `fable`, `nova`, `onyx`, `sage`, `shimmer`.

Available STT models: `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `whisper-1`.
