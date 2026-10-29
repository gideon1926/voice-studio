from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from voice_studio import service


class SpeechTests(unittest.TestCase):
    def test_validation(self):
        for text in (None, "  ", "x" * 10001):
            with self.assertRaises(ValueError):
                service.normalize_text(text)
        self.assertEqual(service.normalize_text(" hello "), "hello")

    def test_document_import(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "script.txt"
            path.write_text("\ufeffHello", encoding="utf-8")
            self.assertEqual(service.read_document(path), "Hello")
            path.write_bytes(b"\xff")
            with self.assertRaisesRegex(ValueError, "UTF-8"):
                service.read_document(path)
            path.write_bytes(b"x" * 100001)
            with self.assertRaisesRegex(ValueError, "100 KB"):
                service.read_document(path)

    def test_invalid_options(self):
        with patch.object(service, "gTTS") as provider:
            for language, accent in [("invalid", "Default"), ("en", "invalid")]:
                with self.assertRaises(ValueError):
                    service.synthesize("hello", language, accent=accent)
            provider.assert_not_called()

    def test_success(self):
        with patch.object(service, "gTTS") as provider:
            provider.return_value.save.side_effect = lambda name: Path(name).write_bytes(b"fake audio")
            path = Path(service.synthesize(" hello ", "en", True, "India"))
            try:
                self.assertEqual(path.read_bytes(), b"fake audio")
                provider.assert_called_once_with(text="hello", lang="en", slow=True, tld="co.in", timeout=(10, 60))
            finally:
                path.unlink()

    def test_failure_cleanup(self):
        paths = []
        def fail(name):
            paths.append(Path(name))
            Path(name).write_bytes(b"partial")
            raise OSError("offline")
        with patch.object(service, "gTTS") as provider:
            provider.return_value.save.side_effect = fail
            with self.assertRaises(RuntimeError):
                service.synthesize("hello")
        self.assertFalse(paths[0].exists())

    def test_empty_audio_rejected(self):
        with patch.object(service, "gTTS"):
            with self.assertRaises(RuntimeError):
                service.synthesize("hello")


if __name__ == "__main__":
    unittest.main()
