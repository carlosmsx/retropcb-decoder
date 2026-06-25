# RetroPCB Decoder

Herramienta de ingeniería inversa de placas PCB a partir de escaneos de alta resolución. Permite navegar la imagen, identificar componentes, trazar pistas y construir un grafo de conectividad — todo desde el browser, sin dependencias de servidor.

---

## Qué hace

A partir de uno o más escaneos de una placa (cara A, cara B, silkscreen) el flujo produce:

1. **Tiles** — la imagen se divide en teselas a múltiples niveles de zoom para navegación fluida
2. **Viewer** — explorador interactivo con capas, componentes, pistas y BOM
3. **Trace editor** — editor vectorial de pistas con detección de conectividad en tiempo real
4. **Grafo de red** — las pistas conectadas forman nets; se puede exportar a KiCad

## Herramientas incluidas

| Archivo | Descripción |
|---|---|
| `viewer.html` | Viewer principal: capas, componentes, pistas, BOM inline |
| `trace_editor.html` | Editor de trazas con snap, Union-Find y URL state |
| `bom.html` | Vista de BOM filtrable |
| `bom_editor.html` | Editor de BOM |
| `place_components.html` | Herramienta de posicionado de componentes |
| `drill_tool.html` | Detección y edición de taladros |
| `crop_tool.html` | Recorte y alineación de escaneos |
| `align_tool.html` | Overlay cara A/B con flip para verificar alineación |

## Inicio rápido

### 1. Crear un proyecto

```bash
python scripts/pcb_init.py "Nombre de la Placa" --slug mi-placa --dpi 600
```

Crea la estructura de carpetas y un `project.json` preconfigurado.

### 2. Agregar imágenes

Colocar los escaneos en `img/`:

```
img/
  pcb_a.png   # cara de componentes
  pcb_b.png   # cara de soldadura
  silk.png    # silkscreen (opcional)
```

### 3. Generar tiles

```bash
python scripts/tiles/generate_tiles.py
```

### 4. Levantar el viewer

```bash
python -m http.server 4174
# abrir http://localhost:4174/
```

## Configuración (`project.json`)

Fuente de verdad de cada instancia. Todos los scripts y el viewer lo leen.

```jsonc
{
  "name": "Mi Placa PCB",
  "slug": "my-pcb",
  "scan": {
    "dpi": 600,
    "layers": [
      { "id": "pcb_a", "label": "Component side (A)", "default": true },
      { "id": "pcb_b", "label": "Solder side (B)" },
      { "id": "silk",  "label": "Silkscreen", "silk": true }
    ]
  },
  "tiles": { "size": 512, "quality": 88 },
  "grid": {
    "pitch_mm": 2.54,
    "pitch_px": null,
    "origin_px": [null, null]
  }
}
```

Los valores `null` en `grid` se calibran midiendo el paso de la grilla en píxeles sobre la imagen.

## Arquitectura

- **Sin backend** — todo corre como archivos estáticos; `python -m http.server` es suficiente para desarrollo
- **Sin framework** — vanilla JS, SVG nativo, CSS custom properties
- **Conectividad de trazas** — Union-Find sobre coordenadas exactas; el snap del editor garantiza que los puntos conectados comparten coordenadas idénticas
- **URL state** — el viewer y el editor serializan zoom, posición y estado en el hash de la URL para compartir vistas

## Requisitos

- Python 3.8+ (pipeline de imágenes: Pillow, OpenCV)
- Cualquier browser moderno (viewer y editor)

```bash
pip install pillow opencv-python numpy
```
