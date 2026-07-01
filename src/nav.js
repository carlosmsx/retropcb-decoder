(() => {
  'use strict';

  const TOOLS = [
    { sep: 'Visualización' },
    { label: 'Viewer',             href: 'viewer.html' },
    { label: 'BOM',                href: 'bom.html' },
    { sep: 'Edición' },
    { label: '1 · Recorte',        href: 'crop_tool.html' },
    { label: '2 · Alineación',     href: 'align_tool.html' },
    { label: '3 · Drills',         href: 'drill_tool.html' },
    { label: '4 · BOM Editor',     href: 'bom_editor.html' },
    { label: '5 · Componentes',    href: 'place_components.html' },
    { label: '6 · Trace Editor',   href: 'trace_editor.html' },
  ];

  const toolName   = document.body.dataset.tool || '';
  const currentPage = location.pathname.split('/').pop() || 'index.html';

  const nav = document.createElement('div');
  nav.className = 'app-nav';
  nav.innerHTML = `
    <a class="app-nav-brand" href="index.html" aria-label="Inicio">
      <svg class="app-nav-icon" viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <rect x="2" y="2" width="16" height="16" rx="2" stroke="currentColor" stroke-width="1.5"/>
        <circle cx="5.5" cy="5.5" r="1.5" fill="currentColor"/>
        <circle cx="14.5" cy="5.5" r="1.5" fill="currentColor"/>
        <circle cx="5.5" cy="14.5" r="1.5" fill="currentColor"/>
        <circle cx="14.5" cy="14.5" r="1.5" fill="currentColor"/>
        <path d="M5.5 5.5 H14.5 M5.5 14.5 H10" stroke="currentColor" stroke-width="1" stroke-linecap="round"/>
      </svg>
      <span class="app-nav-wordmark">RetroPCB Decoder</span>
    </a>
    ${toolName ? `<span class="app-nav-tool-name">${toolName}</span>` : ''}
    <span class="app-nav-gap"></span>
    <div class="app-nav-menu-wrap">
      <button class="app-nav-menu-btn" type="button" aria-haspopup="true" aria-expanded="false">
        Herramientas
        <svg class="app-nav-chevron" viewBox="0 0 12 12" fill="none" aria-hidden="true">
          <path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <ul class="app-nav-dropdown" role="menu" hidden>
        ${TOOLS.map(t => t.sep
          ? `<li class="app-nav-sep" role="presentation">${t.sep}</li>`
          : `<li role="none"><a role="menuitem" href="${t.href}"${currentPage === t.href ? ' class="current" aria-current="page"' : ''}>${t.label}</a></li>`
        ).join('')}
      </ul>
    </div>
  `;

  document.body.prepend(nav);

  const btn = nav.querySelector('.app-nav-menu-btn');
  const dd  = nav.querySelector('.app-nav-dropdown');

  function openMenu() {
    dd.hidden = false;
    btn.setAttribute('aria-expanded', 'true');
  }
  function closeMenu() {
    dd.hidden = true;
    btn.setAttribute('aria-expanded', 'false');
  }

  btn.addEventListener('click', e => {
    e.stopPropagation();
    dd.hidden ? openMenu() : closeMenu();
  });

  document.addEventListener('click', closeMenu);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
})();
