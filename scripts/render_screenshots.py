from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = ROOT / "notebooks"
OUT_DIR = ROOT / "submission" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

SHOT_CONFIG = {
    "01_embeddings_index.ipynb": {
        "output": "nb1_embeddings_index.png",
        "keywords": ["Indexed:", "Top-5:", "Query (paraphrase):"],
    },
    "02_hybrid_search_rrf.ipynb": {
        "output": "nb2_hybrid_search_rrf.png",
        "keywords": ["Precision@10 (avg over", "type", "exact", "mixed"],
    },
    "03_search_api_benchmark.ipynb": {
        "output": "nb3_search_api_benchmark.png",
        "keywords": ["latency_ms:", "top-3 hits:", "Hybrid P99 server-side", "mode"],
    },
    "04_feast_feature_store.ipynb": {
        "output": "nb4_feast_feature_store.png",
        "keywords": ["Wrote 3 Parquet sources", "STDOUT:", "Single lookup:", "Online lookup latency over 100 calls:", "u_001"],
    },
}


def load_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), 22)
    return ImageFont.load_default()


def block_to_text(block: dict) -> str:
    parts: list[str] = []
    for output in block.get("outputs", []):
        if output.get("output_type") == "stream":
            text = output.get("text", "")
            if isinstance(text, list):
                text = "".join(text)
            parts.append(text)
            continue
        if output.get("output_type") in {"execute_result", "display_data"}:
            text = output.get("data", {}).get("text/plain", "")
            if isinstance(text, list):
                text = "".join(text)
            parts.append(text)
            continue
        if output.get("output_type") == "error":
            parts.extend(output.get("traceback", []))
    text = "\n".join(part.rstrip() for part in parts if part)
    return ANSI_RE.sub("", text).strip()


def collect_snippets(nb_path: Path, keywords: list[str]) -> str:
    notebook = json.loads(nb_path.read_text(encoding="utf-8"))
    blocks = [block_to_text(cell) for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    blocks = [block for block in blocks if block]

    selected: list[str] = []
    for keyword in keywords:
        for block in blocks:
            if keyword in block and block not in selected:
                selected.append(block)
                break

    if not selected:
        raise RuntimeError(f"No matching output found in {nb_path.name}")

    return "\n\n".join(selected)


def render_text(text: str, out_path: Path) -> None:
    font = load_font()
    wrapped_lines: list[str] = []
    for line in text.splitlines():
        line = line.rstrip()
        if not line:
            wrapped_lines.append("")
            continue
        wrapped_lines.extend(textwrap.wrap(line, width=110) or [""])

    line_height = 32
    padding = 40
    width = 1800
    height = padding * 2 + max(len(wrapped_lines), 1) * line_height
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    y = padding
    for line in wrapped_lines:
        draw.text((padding, y), line, fill="black", font=font)
        y += line_height
    image.save(out_path)


def main() -> None:
    for notebook_name, config in SHOT_CONFIG.items():
        text = collect_snippets(NOTEBOOKS / notebook_name, config["keywords"])
        render_text(text, OUT_DIR / config["output"])
        print(f"wrote {OUT_DIR / config['output']}")


if __name__ == "__main__":
    main()
