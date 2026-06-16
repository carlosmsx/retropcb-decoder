"""
Genera tiles web (pirámide de zoom) para imágenes grandes de PCB.

Uso básico (toma capas desde project.json):
    python scripts/tiles/generate_tiles.py

Uso con imágenes explícitas:
    python scripts/tiles/generate_tiles.py img/cara_a.png img/cara_b.png

Todos los defaults se pueden sobreescribir via CLI; project.json actúa como
capa de configuración intermedia entre los hardcoded originales y el CLI.
"""

import argparse
import json
import math
import shutil
from pathlib import Path

import cv2


def load_project(project_path):
    p = Path(project_path)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def read_image(path):
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise SystemExit(f"No pude abrir la imagen: {path}")
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    return image


def write_tile(image, path, quality):
    path.parent.mkdir(parents=True, exist_ok=True)
    ok = cv2.imwrite(str(path), image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise SystemExit(f"No pude escribir tile: {path}")


def generate_pyramid(image, out_dir, tile_size, quality):
    height, width = image.shape[:2]
    max_dim = max(width, height)
    max_level = int(math.ceil(math.log(max_dim / tile_size, 2))) if max_dim > tile_size else 0
    levels = []

    for level in range(max_level + 1):
        scale = 2 ** (level - max_level)
        level_width = max(1, int(round(width * scale)))
        level_height = max(1, int(round(height * scale)))
        interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
        level_image = cv2.resize(image, (level_width, level_height), interpolation=interpolation)

        cols = math.ceil(level_width / tile_size)
        rows = math.ceil(level_height / tile_size)
        level_dir = out_dir / str(level)

        for row in range(rows):
            y0 = row * tile_size
            y1 = min(y0 + tile_size, level_height)
            for col in range(cols):
                x0 = col * tile_size
                x1 = min(x0 + tile_size, level_width)
                tile = level_image[y0:y1, x0:x1]
                write_tile(tile, level_dir / f"{col}_{row}.jpg", quality)

        levels.append({
            "level": level,
            "scale": scale,
            "width": level_width,
            "height": level_height,
            "cols": cols,
            "rows": rows,
        })
        print(f"  Nivel {level}: {level_width}x{level_height}, {cols}x{rows} tiles")

    return {
        "width": width,
        "height": height,
        "tileSize": tile_size,
        "maxLevel": max_level,
        "levels": levels,
    }


def default_images_from_project(project):
    """Devuelve lista de rutas de imagen según las capas definidas en project.json."""
    layers = project.get("scan", {}).get("layers", [])
    if not layers:
        return ["img/pcb_a.png", "img/pcb_b.png"]
    return [f"img/{layer['id']}.png" for layer in layers]


def main():
    # Cargamos project.json primero para usarlo como defaults
    # (se puede sobreescribir con --project o cualquier CLI arg)
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--project", default="project.json")
    pre_args, _ = pre.parse_known_args()
    project = load_project(pre_args.project)

    tile_cfg = project.get("tiles", {})
    default_tile_size = tile_cfg.get("size", 512)
    default_quality   = tile_cfg.get("quality", 88)
    default_images    = default_images_from_project(project)

    parser = argparse.ArgumentParser(
        description="Genera tiles web para imágenes grandes de PCB.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--project",   default="project.json",   help="Ruta a project.json")
    parser.add_argument("--tile-size", type=int, default=default_tile_size, help="Tamaño de tile en px (default: %(default)s)")
    parser.add_argument("--quality",   type=int, default=default_quality,   help="Calidad JPEG 0-100 (default: %(default)s)")
    parser.add_argument("--out",       default="tiles",           help="Directorio de salida (default: %(default)s)")
    parser.add_argument("images", nargs="*", default=default_images,
                        help="Imágenes a tilear. Default: capas definidas en project.json")
    args = parser.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    manifest = {"tileSize": args.tile_size, "boards": {}}

    for image_name in args.images:
        image_path = Path(image_name)
        board_id = image_path.stem
        board_dir = out_root / board_id
        if board_dir.exists():
            shutil.rmtree(board_dir)

        print(f"\nGenerando tiles para {image_path} → {board_dir}")
        image = read_image(image_path)
        board_manifest = generate_pyramid(image, board_dir, args.tile_size, args.quality)
        board_manifest["source"] = str(image_path)
        manifest["boards"][board_id] = board_manifest

    manifest_path = out_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest: {manifest_path}")


if __name__ == "__main__":
    main()
