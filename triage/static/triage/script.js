// =========================================================
// Este archivo se carga en TODAS las páginas (desde base.html).
// Antes de usar un elemento revisamos que exista con: if (elemento)
// =========================================================

// 1. MENÚ EN CELULAR (botón ☰): muestra u oculta las opciones
const btnMenu = document.getElementById('btnMenu');
const nav = document.getElementById('nav');
if (btnMenu && nav) {
  btnMenu.addEventListener('click', () => nav.classList.toggle('abierto'));
}

// 2. MENÚ DEL USUARIO (abrir y cerrar)
const btnUsuario = document.getElementById('btnUsuario');
const menuUsuario = document.getElementById('menuUsuario');
if (btnUsuario && menuUsuario) {
  btnUsuario.addEventListener('click', evento => {
    evento.stopPropagation();               // evita que el clic llegue al paso de abajo
    menuUsuario.classList.toggle('abierto');
  });
  // Si haces clic en cualquier otra parte, el menú se cierra
  document.addEventListener('click', () => menuUsuario.classList.remove('abierto'));
}

// 3. FECHA Y HORA ACTUALES (solo en el panel de inicio)
const fechaHoy = document.getElementById('fechaHoy');
if (fechaHoy) {
  const ahora = new Date();
  const fecha = ahora.toLocaleDateString('es-SV', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  const hora = ahora.toLocaleTimeString('es-SV', { hour: '2-digit', minute: '2-digit' });
  fechaHoy.textContent = fecha.charAt(0).toUpperCase() + fecha.slice(1) + ' · ' + hora;
}

// 4. LOS MENSAJES VERDES SE ESCONDEN SOLOS DESPUÉS DE 5 SEGUNDOS
document.querySelectorAll('.mensaje.success').forEach(mensaje => {
  setTimeout(() => {
    mensaje.style.opacity = '0';
    setTimeout(() => mensaje.remove(), 400);
  }, 5000);
});

// 5. FILAS DE TABLA QUE SE PUEDEN TOCAR (tienen data-url)
document.querySelectorAll('tr[data-url]').forEach(fila => {
  fila.style.cursor = 'pointer';
  fila.addEventListener('click', evento => {
    // Si tocó un botón o enlace dentro de la fila, se respeta ese clic
    if (evento.target.closest('a, button, form')) return;
    window.location.href = fila.dataset.url;
  });
});
