import argparse
import re
from pathlib import Path

import numpy as np
from PIL import Image

MAX_DISTANCE = np.sqrt(255 * 255 * 3)


def parse_color(value: str) -> tuple[int, int, int]:
    value = value.strip()
    hex_match = re.fullmatch(r"#?([0-9a-fA-F]{6})", value)
    if hex_match:
        h = hex_match.group(1)
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    parts = [p.strip() for p in value.split(",")]
    if len(parts) == 3:
        r, g, b = (int(p) for p in parts)
        if all(0 <= c <= 255 for c in (r, g, b)):
            return r, g, b

    raise argparse.ArgumentTypeError(
        f"Couleur invalide '{value}' (attendu 'R,G,B' ou '#RRGGBB')"
    )


def generate_painted_images(
    image_path: Path,
    colors_to_paint: list[tuple[int, int, int]],
    sensibility: float,
    output_dir: Path,
) -> list[Path]:
    src = Image.open(image_path).convert("RGB")
    pixels = np.asarray(src, dtype=np.float64)

    orig_v = pixels.max(axis=2) / 255.0
    effective_sensibility = MAX_DISTANCE * sensibility

    already_claimed = np.zeros(pixels.shape[:2], dtype=bool)
    output_paths = []

    output_dir.mkdir(parents=True, exist_ok=True)

    for index, color in enumerate(colors_to_paint, start=1):
        search_vec = np.array(color, dtype=np.float64)
        dist = np.linalg.norm(pixels - search_vec, axis=2)

        match = (dist <= effective_sensibility) & ~already_claimed
        already_claimed |= match

        search_v = max(color) / 255.0
        diff_v = orig_v - search_v
        new_v = np.clip(1.0 + diff_v, 0.0, 1.0)
        final_gray = np.round(new_v * 255).astype(np.uint8)

        out = np.zeros((*pixels.shape[:2], 4), dtype=np.uint8)
        out[..., 0] = final_gray
        out[..., 1] = final_gray
        out[..., 2] = final_gray
        out[..., 3] = np.where(match, 255, 0).astype(np.uint8)

        color_tag = "-".join(str(c) for c in color)
        out_path = output_dir / f"{image_path.stem}_paint_{index}_{color_tag}.png"
        Image.fromarray(out, mode="RGBA").save(out_path)
        output_paths.append(out_path)

    return output_paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Genere, pour chaque couleur de colorsToPaint, une image ne contenant "
            "que les pixels qui seraient repeints (colorsToSet est toujours blanc)."
        )
    )
    parser.add_argument("image", type=Path, help="Chemin de l'image source")
    parser.add_argument(
        "colors",
        nargs="+",
        type=parse_color,
        help="Couleurs a rechercher, ex: 255,0,0 ou #FF0000 (une image generee par couleur)",
    )
    parser.add_argument(
        "-s",
        "--sensibility",
        type=float,
        default=0.1,
        help="Sensibilite (0-1) appliquee comme fraction de la distance couleur max (defaut: 0.1)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Dossier de sortie (defaut: meme dossier que l'image source)",
    )
    args = parser.parse_args()

    output_dir = args.output_dir or args.image.parent

    output_paths = generate_painted_images(
        args.image, args.colors, args.sensibility, output_dir
    )

    for path in output_paths:
        print(path)


if __name__ == "__main__":
    main()
