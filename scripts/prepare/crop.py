"""
Recorta y rectifica una imagen de PCB usando los puntos exportados por crop_tool.html.

El JSON de entrada debe tener el formato:
    {
        "image": "pcb_a.png",
        "points": [
            {"x": 100, "y": 50},   // 1 - superior izquierda
            {"x": 6200, "y": 45},  // 2 - superior derecha
            {"x": 6210, "y": 4400},// 3 - inferior derecha
            {"x": 95, "y": 4410}   // 4 - inferior izquierda
        ],
        "output_width": 6110,
        "output_height": 4360
    }

Uso:
    python scripts/prepare/crop.py pcb_a_crop.json
    python scripts/prepare/crop.py pcb_a_crop.json --out img/pcb_a_cropped.png
    python scripts/prepare/crop.py pcb_a_crop.json --side a   # guarda como img/<slug>_a.png
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_project(root: Path):
    p = root / "project.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def resolve_image(image_name: str, root: Path) -> Path:
    candidates = [
        root / image_name,
        root / "img" / image_name,
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        f"No encontré la imagen '{image_name}'. "
        f"Probé: {', '.join(str(c) for c in candidates)}"
    )


def warp_perspective(image, points, out_w, out_h):
    src = np.float32([[p["x"], p["y"]] for p in points])
    dst = np.float32([
        [0,       0      ],
        [out_w,   0      ],
        [out_w,   out_h  ],
        [0,       out_h  ],
    ])
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(image, M, (out_w, out_h), flags=cv2.INTER_LINEAR)


def main():
    parser = argparse.ArgumentParser(
        description="Recorta y rectifica una imagen de PCB.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("json", help="Archivo JSON exportado por crop_tool.html")
    parser.add_argument("--out", default=None,
                        help="Ruta de salida (default: img/<nombre>_cropped.png)")
    parser.add_argument("--root", default=".",
                        help="Directorio raíz del proyecto (default: .)")
    args = parser.parse_args()

    root      = Path(args.root).resolve()
    json_path = Path(args.json)
    if not json_path.is_absolute():
        json_path = Path.cwd() / json_path

    data = json.loads(json_path.read_text(encoding="utf-8"))

    points   = data["points"]
    out_w    = int(data.get("output_width")  or 0)
    out_h    = int(data.get("output_height") or 0)
    img_name = data.get("image", "")

    if len(points) != 4:
        sys.exit("El JSON necesita exactamente 4 puntos.")

    if out_w <= 0 or out_h <= 0:
        # Estimar dimensiones desde los puntos
        pts = np.float32([[p["x"], p["y"]] for p in points])
        top_w    = np.linalg.norm(pts[1] - pts[0])
        bottom_w = np.linalg.norm(pts[2] - pts[3])
        left_h   = np.linalg.norm(pts[3] - pts[0])
        right_h  = np.linalg.norm(pts[2] - pts[1])
        out_w = int(round((top_w + bottom_w) / 2))
        out_h = int(round((left_h + right_h) / 2))
        print(f"Dimensiones estimadas: {out_w} × {out_h} px")

    img_path = resolve_image(img_name, root)
    print(f"Leyendo: {img_path}")
    img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
    if img is None:
        sys.exit(f"No pude abrir la imagen: {img_path}")

    print(f"Rectificando {img.shape[1]}×{img.shape[0]} → {out_w}×{out_h} px ...")
    result = warp_perspective(img, points, out_w, out_h)

    if args.out:
        out_path = Path(args.out)
    else:
        stem = Path(img_name).stem
        out_path = root / "img" / f"{stem}_cropped.png"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), result)
    print(f"Guardado: {out_path}")


if __name__ == "__main__":
    main()
