// =========================================================
// Este archivo se carga en TODAS las páginas (desde base.html).
// Por eso, antes de usar un elemento, revisamos que exista
// en la página con:  if (elemento) { ... }
// =========================================================

// =========================================================
// 1. MOSTRAR / OCULTAR EL MENÚ LATERAL (botón ☰)
// =========================================================
const contenedor = document.getElementById('contenedor');
document.getElementById('btnMenu').addEventListener('click', () => {
  contenedor.classList.toggle(window.innerWidth <= 600 ? 'menu-abierto' : 'menu-oculto');
});

// =========================================================
// 2. FECHA Y HORA ACTUALES EN EL BANNER (solo en el panel)
// =========================================================
const fecha = document.getElementById('fecha');
const hora = document.getElementById('hora');
if (fecha && hora) {
  const ahora = new Date();
  fecha.textContent = ahora.toLocaleDateString('es-SV', { day: 'numeric', month: 'long', year: 'numeric' });
  hora.textContent = ahora.toLocaleTimeString('es-SV', { hour: '2-digit', minute: '2-digit' });
}

// =========================================================
// 3. OPCIONES DEL MENÚ QUE TODAVÍA NO TIENEN PÁGINA (href="#")
//    Las que sí tienen página (Inicio, Grabación de Audio)
//    abren su página normal y Django marca la opción activa.
// =========================================================
document.querySelectorAll('.menu a').forEach(opcion => {
  opcion.addEventListener('click', evento => {
    if (opcion.getAttribute('href') === '#') {
      evento.preventDefault();                    // no hace nada todavía
      mostrarAviso('Página en construcción: ' + opcion.textContent.trim());
    }
  });
});

// =========================================================
// 4. CAMPANA: QUITAR EL PUNTO ROJO
// =========================================================
const puntoRojo = document.getElementById('puntoRojo');
document.getElementById('btnCampana').addEventListener('click', () => {
  puntoRojo.classList.add('oculto');
  mostrarAviso('No tienes notificaciones nuevas');
});

// =========================================================
// 5. MENÚ DEL USUARIO (abrir y cerrar)
// =========================================================
const btnUsuario = document.getElementById('btnUsuario');
const menuUsuario = document.getElementById('menuUsuario');

btnUsuario.addEventListener('click', evento => {
  evento.stopPropagation();                 // evita que el clic llegue al paso de abajo
  menuUsuario.classList.toggle('abierto');
});

// Si haces clic en cualquier otra parte, el menú se cierra
document.addEventListener('click', () => {
  menuUsuario.classList.remove('abierto');
});

// =========================================================
// 6. BOTONES DE ACCIONES RÁPIDAS Y "VER TODOS" (solo en el panel)
//    Si el botón tiene data-url, abre esa página.
// =========================================================
document.querySelectorAll('.btn-accion').forEach(boton => {
  boton.addEventListener('click', () => {
    if (boton.dataset.url) {
      window.location.href = boton.dataset.url;
    } else {
      mostrarAviso('Abriendo: ' + boton.dataset.accion);
    }
  });
});

const btnVerTodos = document.getElementById('btnVerTodos');
if (btnVerTodos) {
  btnVerTodos.addEventListener('click', () => {
    mostrarAviso('Abriendo la lista completa de pacientes');
  });
}

// =========================================================
// 7. FUNCIÓN QUE MUESTRA EL AVISO ABAJO A LA DERECHA
// =========================================================
const aviso = document.getElementById('aviso');
let temporizador;

function mostrarAviso(texto) {
  aviso.textContent = texto;               // escribe el mensaje
  aviso.classList.add('visible');          // el CSS lo hace aparecer
  clearTimeout(temporizador);              // reinicia la cuenta si ya había uno
  temporizador = setTimeout(() => {
    aviso.classList.remove('visible');     // lo esconde después de 2.5 segundos
  }, 2500);
}
