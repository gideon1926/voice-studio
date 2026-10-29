"""Browser interface and command-line entry point."""
import argparse
from pathlib import Path
import shutil
import gradio as gr
from gtts.lang import tts_langs
from .service import ACCENTS, read_document, synthesize, text_stats


def generate_speech(text, language="en", slow=False, accent="Default"):
    try:
        path = synthesize(text, language, slow, accent)
    except (ValueError, RuntimeError) as exc:
        raise gr.Error(str(exc)) from exc
    return path, path, "Audio ready. Preview or download your MP3."


def import_document(filepath):
    try:
        return read_document(filepath)
    except (ValueError, OSError) as exc:
        raise gr.Error(str(exc)) from exc


def build_app():
    languages = sorted(tts_langs().items(), key=lambda item: item[1])
    with gr.Blocks(title="Voice Studio", delete_cache=(3600, 3600)) as app:
        gr.Markdown("# Voice Studio\n### Give your words a voice.\nCreate multilingual narration for lessons, stories, and everyday listening.")
        with gr.Row():
            with gr.Column(scale=3):
                text = gr.Textbox(label="Your script", lines=12, placeholder="Write or paste your script here...")
                stats = gr.Markdown(text_stats(""))
                upload = gr.File(label="Import a UTF-8 document", file_types=[".txt", ".md"], type="filepath")
                with gr.Row():
                    language = gr.Dropdown(choices=[(name, code) for code, name in languages], value="en", label="Language")
                    accent = gr.Dropdown(choices=list(ACCENTS), value="Default", label="Regional accent", info="Most noticeable for English; availability varies by language.")
                slow = gr.Checkbox(label="Slower narration", value=False)
                with gr.Row():
                    generate = gr.Button("Generate speech", variant="primary")
                    clear = gr.Button("Clear studio")
            with gr.Column(scale=2):
                gr.Markdown("### Listen & export")
                audio = gr.Audio(label="Audio preview", type="filepath")
                download = gr.File(label="Download MP3", interactive=False)
                status = gr.Markdown("Your audio will appear here.")
                gr.Markdown("**How it works**\n1. Write a script or import a document.\n2. Choose a language and narration style.\n3. Generate, listen, and download.\n\n**Privacy**\nText is sent to Google's speech service through gTTS. Internet access is required. Avoid entering confidential information. Temporary audio is scheduled for cleanup after one hour while the app runs.")
        gr.Examples(examples=[["Welcome to Voice Studio. Turn your next idea into something worth listening to.", "en"]], inputs=[text, language])
        text.change(text_stats, text, stats, queue=False)
        upload.upload(import_document, upload, text, queue=False)
        generate.click(generate_speech, [text, language, slow, accent], [audio, download, status], concurrency_limit=2, api_name="synthesize")
        clear.click(lambda: ("", None, None, None, "Your audio will appear here."), outputs=[text, upload, audio, download, status], queue=False)
    return app.queue(max_size=20, default_concurrency_limit=2)


def main():
    parser = argparse.ArgumentParser(description="Voice Studio: multilingual text-to-speech")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--text")
    source.add_argument("--file", type=Path, help="UTF-8 .txt or .md script")
    parser.add_argument("--language", default="en")
    parser.add_argument("--accent", choices=list(ACCENTS), default="Default")
    parser.add_argument("--slow", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("speech.mp3"))
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    if args.text is not None or args.file is not None:
        if args.output.exists():
            parser.error("Output already exists. Choose another --output filename.")
        temporary = None
        try:
            text = read_document(args.file) if args.file is not None else args.text
            temporary = synthesize(text, args.language, args.slow, args.accent)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("xb") as target, open(temporary, "rb") as source_file:
                shutil.copyfileobj(source_file, target)
        except (ValueError, RuntimeError, OSError) as exc:
            parser.exit(1, f"Error: {exc}\n")
        finally:
            if temporary:
                Path(temporary).unlink(missing_ok=True)
        print(f"Saved audio to {args.output.resolve()}")
    else:
        build_app().launch(server_name="127.0.0.1", server_port=args.port)
