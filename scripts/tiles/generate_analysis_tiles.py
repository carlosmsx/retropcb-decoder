"""
Genera capas de análisis tileadas para dos caras de PCB alineadas.

Las capas generadas (contrast, edges, tracks, silk) facilitan la detección
visual de pistas y drills. Los parámetros de imagen se leen desde project.json
y se pueden afinar por CLI.

Uso básico:
    python scripts/tiles/generate_analysis_tiles.py

Con imágenes explícitas:
    python scripts/tiles/generate_analysis_tiles.py --a img/cara_a.png --b img/cara_b.png
"""

import argparse
import json
import math
import shutil
from pathlib import Path

import cv2
import numpy as np


def load_project(project_path):
    p = Path(project_path)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def non_silk_layers(project):
    """Devuelve los IDs de las capas no-silk en orden."""
    layers = project.get("scan", {}).get("layers", [])
    return [l["id"] for l in layers if l.get("id") != "silk" and not l.get("silk")]


def read_image(path):
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise SystemExit(f"No pude abrir la imagen: {path}")
    return image


def read_layer_image(path):
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise SystemExit(f"No pude abrir la imagen de capa extra: {path}")
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.shape[2] == 4:
        alpha = image[:, :, 3].astype(np.float32) / 255.0
        color = image[:, :, :3].astype(np.float32)
        composed = color * alpha[:, :, None]
        return composed.astype(np.uint8)
    return image


def parse_extra_layer(value):
    if "=" not in value:
        raise argparse.ArgumentTypeError("Formato: id=ruta,label,blend,opacity")
    layer_id, payload = value.split("=", 1)
    parts = [p.strip() for p in payload.split(",", 3)]
    if len(parts) != 4 or not all(parts):
        raise argparse.ArgumentTypeError("Formato: id=ruta,label,blend,opacity")
    path, label, blend, opacity_text = parts
    try:
        opacity = float(opacity_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Opacidad inválida: {opacity_text}") from exc
    if not 0 <= opacity <= 1:
        raise argparse.ArgumentTypeError("Opacidad debe estar entre 0 y 1")
    return {"id": layer_id.strip(), "path": path, "label": label.strip('"'), "blend": blend, "opacity": opacity}


def clahe_gray(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    light, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(12, 12))
    return clahe.apply(light)


def make_silkscreen(image, hsv_lower, hsv_upper):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lo = tuple(int(x) for x in hsv_lower)
    hi = tuple(int(x) for x in hsv_upper)
    mask = cv2.inRange(hsv, lo, hi)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    return cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)


def make_trace_contrast(image):
    gray = clahe_gray(image)
    background = cv2.GaussianBlur(gray, (0, 0), 21)
    highpass = cv2.addWeighted(gray, 1.7, background, -0.7, 20)
    highpass = cv2.normalize(highpass, None, 0, 255, cv2.NORM_MINMAX)
    return cv2.cvtColor(highpass, cv2.COLOR_GRAY2BGR)


def make_edges(image, canny_low, canny_high):
    gray = clahe_gray(image)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, canny_low, canny_high)
    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def make_subtle_tracks(image):
    gray = clahe_gray(image)
    inverted = cv2.bitwise_not(gray)
    blur = cv2.GaussianBlur(inverted, (0, 0), 9)
    tracks = cv2.addWeighted(inverted, 1.4, blur, -0.4, 0)
    tracks = cv2.normalize(tracks, None, 0, 255, cv2.NORM_MINMAX)
    _, tracks = cv2.threshold(tracks, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    tracks = cv2.morphologyEx(tracks, cv2.MORPH_OPEN, kernel, iterations=1)
    return cv2.cvtColor(tracks, cv2.COLOR_GRAY2BGR)


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
        level_width  = max(1, int(round(width  * scale)))
        level_height = max(1, int(round(height * scale)))
        level_image = cv2.resize(image, (level_width, level_height), interpolation=cv2.INTER_AREA)
        cols = math.ceil(level_width  / tile_size)
        rows = math.ceil(level_height / tile_size)
        level_dir = out_dir / str(level)

        for row in range(rows):
            y0, y1 = row * tile_size, min((row + 1) * tile_size, level_height)
            for col in range(cols):
                x0, x1 = col * tile_size, min((col + 1) * tile_size, level_width)
                write_tile(level_image[y0:y1, x0:x1], level_dir / f"{col}_{row}.jpg", quality)

        levels.append({"level": level, "scale": scale, "width": level_width, "height": level_height, "cols": cols, "rows": rows})

    return {"width": width, "height": height, "tileSize": tile_size, "maxLevel": max_level, "levels": levels}


def main():
    # Pre-parse para obtener project.json antes de definir defaults del parser principal
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--project", default="project.json")
    pre_args, _ = pre.parse_known_args()
    project = load_project(pre_args.project)

    analysis = project.get("analysis", {})
    tile_cfg  = project.get("tiles", {})
    layer_ids = non_silk_layers(project)

    default_a          = f"img/{layer_ids[0]}.png" if len(layer_ids) > 0 else "img/pcb_a.png"
    default_b          = f"img/{layer_ids[1]}.png" if len(layer_ids) > 1 else "img/pcb_b.png"
    default_tile_size  = tile_cfg.get("size",    512)
    default_quality    = tile_cfg.get("quality",  88)
    default_hsv_lower  = analysis.get("silkscreen_hsv_lower", [0,   0,   145])
    default_hsv_upper  = analysis.get("silkscreen_hsv_upper", [179, 70,  255])
    default_canny_low  = analysis.get("canny_low",   45)
    default_canny_high = analysis.get("canny_high", 130)

    parser = argparse.ArgumentParser(
        description="Genera capas de análisis tileadas para dos caras de PCB.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--project",    default="project.json")
    parser.add_argument("--a",          default=default_a,         help="Imagen cara A (default: %(default)s)")
    parser.add_argument("--b",          default=default_b,         help="Imagen cara B (default: %(default)s)")
    parser.add_argument("--out",        default="analysis_tiles",  help="Directorio de salida")
    parser.add_argument("--tile-size",  type=int,   default=default_tile_size)
    parser.add_argument("--quality",    type=int,   default=default_quality)
    parser.add_argument("--silk-lo",    type=float, nargs=3, default=default_hsv_lower,
                        metavar=("H", "S", "V"), help="HSV mínimo para serigrafia (default: %(default)s)")
    parser.add_argument("--silk-hi",    type=float, nargs=3, default=default_hsv_upper,
                        metavar=("H", "S", "V"), help="HSV máximo para serigrafia (default: %(default)s)")
    parser.add_argument("--canny-low",  type=int,   default=default_canny_low)
    parser.add_argument("--canny-high", type=int,   default=default_canny_high)
    parser.add_argument("--extra-layer", action="append", default=[], type=parse_extra_layer,
                        help="Capa adicional: id=ruta,label,blend,opacity. Repetible.")
    args = parser.parse_args()

    image_a = read_image(args.a)
    image_b = read_image(args.b)
    if image_a.shape[:2] != image_b.shape[:2]:
        raise SystemExit(f"Las imágenes deben tener el mismo tamaño.\n  A: {image_a.shape[:2]}\n  B: {image_b.shape[:2]}")

    # IDs de capa para nombrar outputs (usa los de project.json si están disponibles)
    id_a = layer_ids[0] if len(layer_ids) > 0 else "pcb_a"
    id_b = layer_ids[1] if len(layer_ids) > 1 else "pcb_b"

    def layer_definitions():
        return [
            (f"{id_a}_original",  f"PCB A original",           "normal",   lambda a, b: a),
            (f"{id_b}_original",  f"PCB B original",           "normal",   lambda a, b: b),
            (f"{id_a}_silk",      f"PCB A serigrafia",         "screen",   lambda a, b: make_silkscreen(a, args.silk_lo, args.silk_hi)),
            (f"{id_a}_contrast",  f"PCB A contraste pistas",   "multiply", lambda a, b: make_trace_contrast(a)),
            (f"{id_b}_contrast",  f"PCB B contraste pistas",   "multiply", lambda a, b: make_trace_contrast(b)),
            (f"{id_a}_edges",     f"PCB A bordes",             "screen",   lambda a, b: make_edges(a, args.canny_low, args.canny_high)),
            (f"{id_b}_edges",     f"PCB B bordes",             "screen",   lambda a, b: make_edges(b, args.canny_low, args.canny_high)),
            (f"{id_a}_tracks",    f"PCB A mascara pistas",     "screen",   lambda a, b: make_subtle_tracks(a)),
            (f"{id_b}_tracks",    f"PCB B mascara pistas",     "screen",   lambda a, b: make_subtle_tracks(b)),
        ]

    out_root = Path(args.out)
    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "tileSize": args.tile_size,
        "width":  int(image_a.shape[1]),
        "height": int(image_a.shape[0]),
        "layers": {},
        "presets": [
            {"id": "original_overlay", "label": "Original A+B",
             "layers": [{"id": f"{id_a}_original", "opacity": 1,    "blend": "normal"},
                        {"id": f"{id_b}_original", "opacity": 0.5,  "blend": "normal"}]},
            {"id": "silk_only",        "label": "Serigrafia",
             "layers": [{"id": f"{id_a}_silk",     "opacity": 0.85, "blend": "screen"}]},
            {"id": "tracks_compare",   "label": "Pistas realzadas",
             "layers": [{"id": f"{id_a}_contrast", "opacity": 1,    "blend": "normal"},
                        {"id": f"{id_b}_contrast", "opacity": 0.55, "blend": "difference"},
                        {"id": f"{id_a}_edges",    "opacity": 0.35, "blend": "screen"},
                        {"id": f"{id_b}_edges",    "opacity": 0.35, "blend": "screen"}]},
            {"id": "track_masks",      "label": "Mascaras de pistas",
             "layers": [{"id": f"{id_a}_tracks",   "opacity": 0.75, "blend": "screen"},
                        {"id": f"{id_b}_tracks",   "opacity": 0.75, "blend": "screen"}]},
        ],
    }

    for layer_id, label, default_blend, factory in layer_definitions():
        print(f"Generando capa {layer_id}...")
        layer_image = factory(image_a, image_b)
        layer_manifest = generate_pyramid(layer_image, out_root / layer_id, args.tile_size, args.quality)
        layer_manifest["label"] = label
        layer_manifest["defaultBlend"] = default_blend
        manifest["layers"][layer_id] = layer_manifest

    for extra in args.extra_layer:
        layer_id = extra["id"]
        print(f"Generando capa extra {layer_id}...")
        layer_image = read_layer_image(Path(extra["path"]))
        if layer_image.shape[:2] != image_a.shape[:2]:
            raise SystemExit(f"La capa extra {layer_id} no coincide en tamaño con las imágenes principales.")
        layer_dir = out_root / layer_id
        if layer_dir.exists():
            shutil.rmtree(layer_dir)
        layer_manifest = generate_pyramid(layer_image, layer_dir, args.tile_size, args.quality)
        layer_manifest["label"]        = extra["label"]
        layer_manifest["defaultBlend"] = extra["blend"]
        layer_manifest["source"]       = extra["path"]
        manifest["layers"][layer_id]   = layer_manifest

    manifest_path = out_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest: {manifest_path}")
    print(f"Capas generadas: {list(manifest['layers'].keys())}")


if __name__ == "__main__":
    main()
