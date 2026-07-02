"""
Aplica el alineamiento exportado por align_tool.html a ambos lados del PCB.

Lee align.json y genera imágenes alineadas listas para tilosear:
    img/side_a_aligned.png
    img/side_b_aligned.png

El campo "alignment" (futuro) soportará una homografía 3x3 para corrección fina.

Uso:
    python scripts/prepare/apply_align.py
    python scripts/prepare/apply_align.py --align align.json
    python scripts/prepare/apply_align.py --align align.json --root .
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def resolve_image(name: str, root: Path) -> Path:
    for candidate in [root / name, root / "img" / name]:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"No encontré '{name}'. Probé: {root / name}, {root / 'img' / name}"
    )


def apply_flip(img, flip_h: bool, flip_v: bool):
    if flip_h and flip_v:
        return cv2.flip(img, -1)
    if flip_h:
        return cv2.flip(img, 1)
    if flip_v:
        return cv2.flip(img, 0)
    return img


def apply_homography(img, H_data, ref_shape):
    """Aplica una homografía 3x3 para alinear la imagen a la referencia."""
    H = np.array(H_data, dtype=np.float64)
    h, w = ref_shape[:2]
    return cv2.warpPerspective(img, H, (w, h), flags=cv2.INTER_LINEAR)


def pad_to(img, target_w: int, target_h: int) -> np.ndarray:
    """Añade padding negro a la derecha y abajo hasta alcanzar target_w × target_h."""
    h, w = img.shape[:2]
    if w == target_w and h == target_h:
        return img
    channels = img.shape[2] if img.ndim == 3 else 1
    canvas = np.zeros((target_h, target_w, channels), dtype=img.dtype)
    canvas[:h, :w] = img
    return canvas


def save(img, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), img)
    print(f"  → {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Aplica flip y alineamiento a ambos lados del PCB.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--align", default="align.json",
                        help="JSON exportado por align_tool.html (default: align.json)")
    parser.add_argument("--root", default=".",
                        help="Directorio raíz del proyecto (default: .)")
    parser.add_argument("--suffix", default="_aligned",
                        help="Sufijo para los archivos de salida (default: _aligned)")
    args = parser.parse_args()

    root       = Path(args.root).resolve()
    align_path = Path(args.align)
    if not align_path.is_absolute():
        align_path = Path.cwd() / align_path

    data = json.loads(align_path.read_text(encoding="utf-8"))

    side_a  = data.get("side_a")
    side_b  = data.get("side_b")
    flip_h  = bool(data.get("flip_h", False))
    flip_v  = bool(data.get("flip_v", False))
    align   = data.get("alignment")  # None o dict con "homography"

    if not side_a and not side_b:
        sys.exit("align.json no tiene side_a ni side_b.")

    out_dir = root / "img"

    # ── Lado A ──────────────────────────────────────────────
    img_a = None
    stem_a = None
    if side_a:
        path_a = resolve_image(side_a, root)
        print(f"Leyendo lado A: {path_a}")
        img_a = cv2.imread(str(path_a), cv2.IMREAD_COLOR)
        if img_a is None:
            sys.exit(f"No pude abrir: {path_a}")
        stem_a = Path(side_a).stem

    # ── Lado B ──────────────────────────────────────────────
    img_b = None
    stem_b = None
    if side_b:
        path_b = resolve_image(side_b, root)
        print(f"Leyendo lado B: {path_b}")
        img_b = cv2.imread(str(path_b), cv2.IMREAD_COLOR)
        if img_b is None:
            sys.exit(f"No pude abrir: {path_b}")
        stem_b = Path(side_b).stem

        if flip_h or flip_v:
            print(f"  flip_h={flip_h}  flip_v={flip_v}")
            img_b = apply_flip(img_b, flip_h, flip_v)

        if align and "homography" in align:
            if img_a is None:
                sys.exit("Se necesita side_a como referencia para aplicar la homografía.")
            print("  Aplicando homografía de alineamiento fino...")
            img_b = apply_homography(img_b, align["homography"], img_a.shape)

    # ── Canonicalizar dimensiones ────────────────────────────
    size_mode   = data.get("size_mode", "natural")
    output_size = data.get("output_size")  # {"w": ..., "h": ...} o None

    if img_a is not None and img_b is not None:
        wA, hA = img_a.shape[1], img_a.shape[0]
        wB, hB = img_b.shape[1], img_b.shape[0]

        if size_mode == "natural":
            # Padding al máximo para que compartan el mismo espacio de coord.
            target_w = max(wA, wB)
            target_h = max(hA, hB)
        elif output_size:
            target_w = int(output_size["w"])
            target_h = int(output_size["h"])
        else:
            target_w, target_h = wA, hA  # fallback a tamaño A

        print(f"  Modo '{size_mode}' → {target_w}×{target_h} px")

        if (wA, hA) != (target_w, target_h):
            if size_mode == "natural":
                img_a = pad_to(img_a, target_w, target_h)
            else:
                img_a = cv2.resize(img_a, (target_w, target_h), interpolation=cv2.INTER_AREA)

        if (wB, hB) != (target_w, target_h):
            if size_mode == "natural":
                img_b = pad_to(img_b, target_w, target_h)
            else:
                img_b = cv2.resize(img_b, (target_w, target_h), interpolation=cv2.INTER_AREA)

    # ── Guardar ──────────────────────────────────────────────
    if img_a is not None:
        save(img_a, out_dir / f"{stem_a}{args.suffix}.png")
    if img_b is not None:
        save(img_b, out_dir / f"{stem_b}{args.suffix}.png")

    print("Listo.")


if __name__ == "__main__":
    main()
