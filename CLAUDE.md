# PCB Reverser — Instrucciones para Claude Code

Herramienta genérica de ingeniería inversa de placas PCB.
Derivada del proyecto [MSX DPC-200](../msx/dpc200) y diseñada para funcionar
con cualquier PCB a partir de escaneos de alta resolución.

---

## Estado del proyecto

### Completado

**Fase 1 — Esqueleto**
- Estructura de carpetas (`data/`, `tiles/`, `img/`, `src/`, `scripts/`, `archive/`)
- `project.json` como fuente de verdad para toda la configuración de instancia
- Git inicializado, `.gitignore` configurado (los tiles NO van a git, `/tiles/`)

**Fase 2 — Viewer genérico**
- `viewer.html` — lee layers desde `project.json`; board selector generado dinámicamente; sin referencias al DPC200
- `bom.html`, `trace_editor.html`, `index.html` — ídem, todos leen `project.json`
- `src/styles.css`, `src/i18n.js` — copiados y desacoplados del DPC200

**Fase 3 — Pipeline de imágenes**
- `scripts/pcb_init.py` — crea un proyecto nuevo desde cero (estructura + `project.json` template)
- `scripts/tiles/generate_tiles.py` — genera tiles web desde imágenes; lee capas y config desde `project.json`
- `scripts/tiles/generate_analysis_tiles.py` — genera capas de análisis (contrast, edges, tracks, silk); todos los parámetros de imagen vienen de `project.json`

### Pendiente

**Fase 4 — Pipeline de datos (onboarding parte 2)**
Ver checklist completo abajo. Tareas principales:
- [ ] Copiar scripts de detección de drills a `scripts/analysis/` y parametrizar con `project.json`
- [ ] Crear herramienta de calibración de grilla (hoy `grid.pitch_px` y `grid.origin_px` se ponen a mano)
- [ ] Documentar el schema de `data/components.json` como estándar
- [ ] Copiar `data/ic_pinouts.json` del DPC200 como librería genérica de referencia
- [ ] Copiar JS tools de `tools/` del DPC200 (build_points, build_segments, build_bom, export_kicad)
- [ ] Prueba end-to-end con placa real: drills → componentes → BOM mínimo visible en el viewer

**Fase 5 — Deploy y transferencia del DPC200**
- [ ] Configurar deploy (Vercel / GitHub Pages)
- [ ] Crear instancia del DPC200 dentro de este framework (copiar data/, tiles/ del repo dpc200)
- [ ] Limpiar el repo dpc200 original (cosas/, duplicados, __pycache__)
- [ ] README con el proceso de onboarding completo

---

## Arquitectura clave

### `project.json`

Es la fuente de verdad de toda instancia. Todos los scripts y el viewer lo leen.

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
    "pitch_px": null,        // calibrar: DPI * 2.54 / 25.4
    "origin_px": [null, null]
  },
  "analysis": {
    "silkscreen_hsv_lower": [0, 0, 145],
    "silkscreen_hsv_upper": [179, 70, 255],
    "drill_dark_value": 52,
    "drill_min_radius": 1.8,
    "drill_max_radius": 16,
    "drill_min_circularity": 0.5,
    "canny_low": 45,
    "canny_high": 130
  }
}
```

Los valores `null` en `grid` son los que hay que calibrar por placa.

### Viewer y capas

El viewer lee `project.json` al arrancar y construye el selector de capas dinámicamente.
Los IDs de capa (`pcb_a`, `pcb_b`, `silk`) ya no están hardcodeados — vienen de `scan.layers`.
La lógica interna usa `state.layerIds[]` y `state.silkId` en vez de strings literales.

### Scripts de tiles

Ambos scripts hacen pre-parse de `--project` para leer defaults ANTES de definir el parser
principal — así los defaults del `--help` ya muestran los valores de `project.json`.

---

## Cómo levantar el viewer

```powershell
cd C:\workspace\pcb_reverser
python -m http.server 4174
# abrir http://localhost:4174/
```

Sin tiles el viewer muestra "Faltan tiles" — eso es el comportamiento correcto hasta
que se corra `generate_tiles.py` con imágenes reales.

## Cómo iniciar un nuevo proyecto

```powershell
python scripts/pcb_init.py "Nombre de la Placa" --slug mi-placa --dpi 600
# coloca las imágenes en img/ y corre generate_tiles.py
```

---

## Repo de referencia

El proyecto DPC200 original está en `C:\workspace\msx\dpc200`.
Es la fuente de los scripts de análisis, los JS tools, la librería `ic_pinouts.json`,
y el ejemplo completo de `data/components.json` y `data/traces.json`.
Los scripts de análisis relevantes están en `dpc200/cosas/pcb_analysis/scripts/`.
Los JS tools de build están en `dpc200/tools/`.
