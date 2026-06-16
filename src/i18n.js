/**
 * i18n.js — Internacionalización ES / EN para DPC200
 * Uso: incluir en <head> (sin defer). Expone window.I18N.
 */
(function () {
  'use strict';

  const STRINGS = {
    es: {
      /* nav */
      'nav.guide'          : 'Guía',
      /* crt */
      'crt.tagline'        : 'Archivo técnico abierto',
      /* hero */
      'hero.cta'           : 'Explorar motherboard',
      'hero.bom'           : 'Ver lista de componentes',
      /* guide section */
      'guide.eyebrow'      : 'Guía rápida',
      'guide.title'        : 'Cómo usar el viewer',
      'guide.1.title'      : 'Navegar',
      'guide.1.body'       : 'Arrastrá para mover el tablero. Usá la rueda del mouse o pellizco en pantalla táctil para zoom. Los botones <em class="guide-kbd">+</em> <em class="guide-kbd">−</em> y <em class="guide-kbd">⊡</em> ajustan la vista.',
      'guide.2.title'      : 'Capas',
      'guide.2.body'       : 'Los botones de la barra activan y desactivan capas: ICs, conectores, capacitores, resistencias, inductores, pistas y más. Podés combinarlas libremente.',
      'guide.3.title'      : 'Componentes',
      'guide.3.body'       : 'Pasá el cursor sobre cualquier pieza para ver su referencia, valor y tipo. En los ICs, cada pin muestra su nombre y función.',
      'guide.4.title'      : 'Buscar',
      'guide.4.body'       : 'El botón <em class="guide-kbd">buscar</em> abre un cuadro de búsqueda. Escribí la referencia de un componente, por ejemplo <em class="guide-kbd">U4</em> o <em class="guide-kbd">C17</em>, para centrarlo en pantalla.',
      'guide.cta'          : 'Abrir el viewer',
      /* footer */
      'footer.tagline'     : 'Archivo técnico independiente',
      'footer.by'          : 'Investigación y documentación por',
      /* viewer — toolbar titles */
      'tb.silk.title'      : 'Serigrafia',
      'tb.drill.title'     : 'Taladros comunes',
      'tb.con.title'       : 'Conectores',
      'tb.caps.title'      : 'Capacitores',
      'tb.res.title'       : 'Resistencias',
      'tb.dio.title'       : 'Diodos',
      'tb.ind.title'       : 'Inductores',
      'tb.xtal.title'      : 'Cristal',
      'tb.trace-a.title'   : 'Pistas cara A',
      'tb.trace-b.title'   : 'Pistas cara B',
      'tb.fit.title'       : 'Ajustar vista',
      'tb.search.title'    : 'Buscar componente',
      /* viewer — toolbar labels */
      'tb.trace-a.label'   : 'pistas A',
      'tb.trace-b.label'   : 'pistas B',
      'tb.search.label'    : 'buscar',
      /* viewer — opacity */
      'opacity.title'      : 'Opacidad capa B',
      /* viewer — search dialog */
      'search.dialog-title': 'Buscar componente',
      'search.placeholder' : 'ej: R53, C12, U4…',
      'search.cancel'      : 'Cancelar',
      'search.ok'          : 'Ir',
      'search.not-found'   : 'No se encontró',
      /* viewer — JS type labels */
      'type.IC'            : 'Integrado',
      'type.CAP'           : 'Capacitor',
      'type.RES'           : 'Resistencia',
      'type.DIO'           : 'Diodo',
      'type.IND'           : 'Inductor',
      'type.XTAL'          : 'Cristal',
      'type.JP'            : 'Jumper',
      'type.RELAY'         : 'Relay',
      'type.RNET'          : 'Red de res.',
      'type.CON'           : 'Conector',
      'type.CON50'         : 'Conector',
      'type.VIA'           : 'Via',
      /* viewer — layer group labels */
      'lg.view'            : 'Vista',
      'lg.chips'           : 'Chips',
      'lg.connectors'      : 'Conectores',
      'lg.passives'        : 'Pasivos',
      'lg.traces'          : 'Pistas',
    },

    en: {
      /* nav */
      'nav.guide'          : 'Guide',
      /* crt */
      'crt.tagline'        : 'Open technical archive',
      /* hero */
      'hero.cta'           : 'Explore motherboard',
      'hero.bom'           : 'View component list',
      /* guide section */
      'guide.eyebrow'      : 'Quick guide',
      'guide.title'        : 'How to use the viewer',
      'guide.1.title'      : 'Navigate',
      'guide.1.body'       : 'Drag to pan the board. Use the mouse wheel or pinch gesture to zoom. The <em class="guide-kbd">+</em> <em class="guide-kbd">−</em> and <em class="guide-kbd">⊡</em> buttons adjust the view.',
      'guide.2.title'      : 'Layers',
      'guide.2.body'       : 'The toolbar buttons toggle layers on and off: ICs, connectors, capacitors, resistors, inductors, traces and more. Combine them freely.',
      'guide.3.title'      : 'Components',
      'guide.3.body'       : 'Hover over any part to see its reference, value and type. On ICs, each pin shows its name and function.',
      'guide.4.title'      : 'Search',
      'guide.4.body'       : 'The <em class="guide-kbd">search</em> button opens a search box. Type a component reference, for example <em class="guide-kbd">U4</em> or <em class="guide-kbd">C17</em>, to center it on screen.',
      'guide.cta'          : 'Open the viewer',
      /* footer */
      'footer.tagline'     : 'Independent technical archive',
      'footer.by'          : 'Research and documentation by',
      /* viewer — toolbar titles */
      'tb.silk.title'      : 'Silkscreen',
      'tb.drill.title'     : 'Common drills',
      'tb.con.title'       : 'Connectors',
      'tb.caps.title'      : 'Capacitors',
      'tb.res.title'       : 'Resistors',
      'tb.dio.title'       : 'Diodes',
      'tb.ind.title'       : 'Inductors',
      'tb.xtal.title'      : 'Crystal',
      'tb.trace-a.title'   : 'Traces side A',
      'tb.trace-b.title'   : 'Traces side B',
      'tb.fit.title'       : 'Fit view',
      'tb.search.title'    : 'Search component',
      /* viewer — toolbar labels */
      'tb.trace-a.label'   : 'traces A',
      'tb.trace-b.label'   : 'traces B',
      'tb.search.label'    : 'search',
      /* viewer — opacity */
      'opacity.title'      : 'Layer B opacity',
      /* viewer — search dialog */
      'search.dialog-title': 'Search component',
      'search.placeholder' : 'e.g.: R53, C12, U4…',
      'search.cancel'      : 'Cancel',
      'search.ok'          : 'Go',
      'search.not-found'   : 'Not found',
      /* viewer — JS type labels */
      'type.IC'            : 'IC',
      'type.CAP'           : 'Capacitor',
      'type.RES'           : 'Resistor',
      'type.DIO'           : 'Diode',
      'type.IND'           : 'Inductor',
      'type.XTAL'          : 'Crystal',
      'type.JP'            : 'Jumper',
      'type.RELAY'         : 'Relay',
      'type.RNET'          : 'Resistor array',
      'type.CON'           : 'Connector',
      'type.CON50'         : 'Connector',
      'type.VIA'           : 'Via',
      /* viewer — layer group labels */
      'lg.view'            : 'View',
      'lg.chips'           : 'Chips',
      'lg.connectors'      : 'Connectors',
      'lg.passives'        : 'Passives',
      'lg.traces'          : 'Traces',
    },
  };

  /* ── Core helpers ── */

  function getLang() {
    const stored = localStorage.getItem('pcb-reverser-lang');
    if (stored === 'en' || stored === 'es') return stored;
    return (navigator.language || '').toLowerCase().startsWith('en') ? 'en' : 'es';
  }

  function t(key, lang) {
    const l = lang || getLang();
    return (STRINGS[l] && STRINGS[l][key]) || (STRINGS.es && STRINGS.es[key]) || key;
  }

  function applyLang(lang) {
    localStorage.setItem('pcb-reverser-lang', lang);
    document.documentElement.lang = lang === 'en' ? 'en' : 'es';

    document.querySelectorAll('[data-i18n]').forEach(el => {
      const v = t(el.dataset.i18n, lang);
      if (v) el.textContent = v;
    });

    document.querySelectorAll('[data-i18n-html]').forEach(el => {
      const v = t(el.dataset.i18nHtml, lang);
      if (v) el.innerHTML = v;
    });

    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const v = t(el.dataset.i18nTitle, lang);
      if (v) el.title = v;
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const v = t(el.dataset.i18nPlaceholder, lang);
      if (v) el.placeholder = v;
    });

    document.querySelectorAll('[data-i18n-aria]').forEach(el => {
      const v = t(el.dataset.i18nAria, lang);
      if (v) el.setAttribute('aria-label', v);
    });

    /* update lang switcher buttons */
    document.querySelectorAll('[data-lang]').forEach(btn => {
      btn.classList.toggle('lang-active', btn.dataset.lang === lang);
    });

    /* notify other scripts */
    document.dispatchEvent(new CustomEvent('langchange', { detail: { lang } }));
  }

  /* ── Expose API ── */
  window.I18N = { getLang, applyLang, t };

  /* ── Boot on DOM ready ── */
  document.addEventListener('DOMContentLoaded', function () {
    const lang = getLang();
    applyLang(lang);
    document.querySelectorAll('[data-lang]').forEach(btn => {
      btn.addEventListener('click', function () { applyLang(this.dataset.lang); });
    });
  });
})();
