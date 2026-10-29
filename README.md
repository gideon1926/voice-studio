# Voice Studio

A multilingual text-to-speech studio built with Python, Gradio, and gTTS. Write a script, import a document, preview narration, and download an MP3.

## Features

- Searchable language selector populated from gTTS
- Regional accents and slower narration
- UTF-8 text and Markdown document import
- Live character, word, and estimated narration-duration statistics
- Audio preview and MP3 download
- Browser interface and command-line conversion
- Bounded request queue, input limits, network timeouts, and actionable errors
- Automated offline tests and GitHub Actions checks

## Quick start

Use Python 3.11 or newer. CI uses Python 3.12.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-tts.txt
python text_to_speech.py
```

Open http://127.0.0.1:7860. On macOS/Linux, activate with `source .venv/bin/activate`.

## Command line

```powershell
python -m voice_studio --text "Welcome to Voice Studio" --language en --output welcome.mp3
python -m voice_studio --file script.txt --language ta --slow --output narration.mp3
python -m voice_studio --port 7861
```

Existing output files are never overwritten. Documents must be UTF-8 `.txt` or `.md`, at most 100 KB, with up to 10,000 characters. Markdown is spoken as plain text.

## Development

```powershell
python -m unittest discover -s tests -v
```

`voice_studio/service.py` handles validation and synthesis. `voice_studio/app.py` contains the UI and CLI. `text_to_speech.py` is the launcher.

## Privacy and limitations

Text is sent to Google's online speech service through gTTS. Internet is required. Availability, pronunciation, accent support, and rate limits depend on the provider. There is no voice cloning or arbitrary pitch control. Duration is a rough estimate based on 150 words per minute, which varies by language.

The UI binds to localhost for personal use. Add authentication and deployment controls before exposing it publicly. Gradio schedules generated audio for cleanup after an hour while the app runs. User downloads remain on disk; abrupt shutdown can leave files in the OS temporary directory. CLI conversions remove their intermediate audio immediately.

## References

- [Gradio Blocks](https://www.gradio.app/docs/gradio/blocks)
- [gTTS documentation](https://gtts.readthedocs.io/)
