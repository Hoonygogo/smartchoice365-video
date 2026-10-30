"""Download pinned public Supertonic assets. No account, token, or card needed."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import urllib.request

REVISION = "3cadd1ee6394adea1bd021217a0e650ede09a323"
FILES = ["LICENSE", "voice_styles/F1.json", "onnx/tts.json", "onnx/unicode_indexer.json",
         "onnx/duration_predictor.onnx", "onnx/text_encoder.onnx",
         "onnx/vector_estimator.onnx", "onnx/vocoder.onnx"]


def download_model(destination):
    destination = Path(destination)
    def download(name):
        path = destination / name
        if path.is_file() and path.stat().st_size:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".part")
        url = f"https://huggingface.co/Supertone/supertonic-3/resolve/{REVISION}/{name}"
        try:
            with urllib.request.urlopen(url, timeout=120) as response, tmp.open("wb") as out:
                while chunk := response.read(1024 * 1024):
                    out.write(chunk)
            tmp.replace(path)
            print(f"Downloaded {name}", flush=True)
        finally:
            tmp.unlink(missing_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(download, FILES))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", default=".models/supertonic-3")
    download_model(parser.parse_args().destination)

