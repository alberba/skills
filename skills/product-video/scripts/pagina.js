// Se inyecta antes que cualquier script de la página (add_init_script).
// __CSS__ lo sustituye el grabador por pagina.css más el CSS de escenas.py.
(() => {
  const css = __CSS__;
  // El estilo entra antes del primer pintado, no al cargar el DOM.
  const st = document.createElement('style'); st.textContent = css;
  const attach = () => {
    const html = document.documentElement;
    if (!html) return false;
    html.appendChild(st);
    return true;
  };
  if (!attach()) {
    new MutationObserver((_, o) => { if (attach()) o.disconnect(); }).observe(document, { childList: true });
  }
  const boot = () => {
    if (document.getElementById('rec-cursor')) return;
    const c = document.createElement('div'); c.id = 'rec-cursor'; document.body.appendChild(c);
    const pos = JSON.parse(sessionStorage.getItem('rec-cursor') || '[-50,-50]');
    c.style.left = pos[0] + 'px'; c.style.top = pos[1] + 'px';
    addEventListener('mousemove', e => {
      c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px';
      sessionStorage.setItem('rec-cursor', JSON.stringify([e.clientX, e.clientY]));
    }, true);
    addEventListener('mousedown', () => c.classList.add('down'), true);
    addEventListener('mouseup', () => c.classList.remove('down'), true);
    const modes = JSON.parse(sessionStorage.getItem('rec-modes') || '[]');
    document.documentElement.classList.add(...modes);

  };
  if (document.body) boot(); else document.addEventListener('DOMContentLoaded', boot);
})();
