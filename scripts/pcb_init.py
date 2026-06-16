"""
Inicializa un nuevo proyecto de ingeniería inversa de PCB.

Crea la estructura de carpetas estándar y un project.json pre-configurado
listo para completar con los datos del escaneo.

Uso:
    python scripts/pcb_init.py "Mi Placa Ejemplo" --slug mi-placa --dpi 600

El slug se usa para nombrar los archivos de imagen esperados:
    img/<slug>_a.png   (cara componentes)
    img/<slug>_b.png   (cara soldadura)
    img/<slug>_silk.png (serigrafia, opcional)
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Windows: forzar UTF-8 en stdout para que los acentos se vean bien
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


DIRS = [
    "img",
    "data",
    "data/graph",
    "data/pinouts",
    "data/export",
    "tiles",
    "scripts/tiles",
    "scripts/analysis",
    "archive",
]

PROJECT_TEMPLATE = {
    "name": None,          # se rellena con el argumento
    "slug": None,          # se rellena con el argumento
    "description": "",

    "scan": {
        "dpi": None,       # se rellena con --dpi
        "layers": None,    # se genera según el slug
    },

    "tiles": {
        "size": 512,
        "quality": 88,
        "format": "jpg"
    },

    "grid": {
        "pitch_mm": 2.54,
        "pitch_px": None,       # calibrar manualmente (ver onboarding)
        "origin_px": [None, None]
    },

    "analysis": {
        "silkscreen_hsv_lower": [0, 0, 145],
        "silkscreen_hsv_upper": [179, 70, 255],
        "drill_dark_value": 52,
        "drill_min_radius": 1.8,
        "drill_max_radius": 16,
        "drill_min_circularity": 0.5,
        "drill_min_fill": 0.38,
        "canny_low": 45,
        "canny_high": 130
    },

    "deploy": {
        "base_url": ""
    }
}

NEXT_STEPS = """
Próximos pasos:
  1. Colocar los escaneos en img/:
       img/{slug}_a.png    (cara componentes, {dpi} DPI)
       img/{slug}_b.png    (cara soldadura, {dpi} DPI)
       img/{slug}_silk.png (serigrafia, opcional)

  2. Generar tiles:
       python scripts/tiles/generate_tiles.py

  3. Abrir el viewer y verificar:
       python -m http.server 4174
       http://localhost:4174/viewer.html

  4. Calibrar la grilla en project.json:
       grid.origin_px  =coordenadas del primer pad (en pixels)
       grid.pitch_px   =distancia entre pads (2.54mm en pixels a {dpi}dpi = {pitch_px:.1f}px)

  5. Generar capas de análisis:
       python scripts/tiles/generate_analysis_tiles.py
"""


def slugify(name):
    """Convierte un nombre a slug simple."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug.strip("-")


def make_layers(slug):
    return [
        {"id": f"{slug}_a",    "label": "Component side (A)", "default": True},
        {"id": f"{slug}_b",    "label": "Solder side (B)"},
        {"id": f"{slug}_silk", "label": "Silkscreen", "silk": True},
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Inicializa un nuevo proyecto de ingeniería inversa de PCB.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("name",  help="Nombre del proyecto, ej: 'MSX SVI-738'")
    parser.add_argument("--slug", default=None,
                        help="Slug para nombres de archivo (default: derivado del nombre)")
    parser.add_argument("--dpi", type=int, default=600,
                        help="DPI del escaneo (default: 600)")
    parser.add_argument("--out", default=".",
                        help="Directorio raíz del proyecto (default: directorio actual)")
    args = parser.parse_args()

    slug = args.slug or slugify(args.name)
    out  = Path(args.out).resolve()

    # Verificar que no sobreescriba un proyecto existente
    project_file = out / "project.json"
    if project_file.exists():
        data = json.loads(project_file.read_text(encoding="utf-8"))
        if data.get("slug") and data["slug"] != slug:
            print(f"AVISO: Ya existe project.json con slug '{data['slug']}'. No se sobreescribe.")
            sys.exit(0)

    # Crear directorios
    print(f"Inicializando proyecto: {args.name!r} (slug: {slug})")
    print(f"Directorio: {out}")
    print()
    for d in DIRS:
        (out / d).mkdir(parents=True, exist_ok=True)
        print(f"  +{d}/")

    # pitch_px = dpi * 2.54 / 25.4 = dpi * 0.1
    pitch_px = round(args.dpi * 2.54 / 25.4, 2)

    # Escribir project.json
    project = json.loads(json.dumps(PROJECT_TEMPLATE))  # deep copy
    project["name"]  = args.name
    project["slug"]  = slug
    project["scan"]["dpi"]    = args.dpi
    project["scan"]["layers"] = make_layers(slug)

    project_file.write_text(
        json.dumps(project, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"\n  +project.json")

    # Mostrar próximos pasos
    print()
    print(NEXT_STEPS.format(slug=slug, dpi=args.dpi, pitch_px=pitch_px))


if __name__ == "__main__":
    main()
