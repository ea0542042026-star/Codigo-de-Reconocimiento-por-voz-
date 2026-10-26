// =========================================================
// 1. MOSTRAR / OCULTAR EL MENÚ LATERAL (botón ☰)
// =========================================================
const contenedor = document.getElementById('contenedor');
document.getElementById('btnMenu').addEventListener('click', () => {
  contenedor.classList.toggle(window.innerWidth <= 600 ? 'menu-abierto' : 'menu-oculto');
});

// =========================================================
// 2. FECHA Y HORA ACTUALES EN EL BANNER
// =========================================================
const ahora = new Date();
document.getElementById('fecha').textContent =
  ahora.toLocaleDateString('es-SV', { day: 'numeric', month: 'long', year: 'numeric' });
document.getElementById('hora').textContent =
  ahora.toLocaleTimeString('es-SV', { hour: '2-digit', minute: '2-digit' });

// =========================================================
// 3. MARCAR LA OPCIÓN DEL MENÚ QUE SE HIZO CLIC
// =========================================================
const opcionesMenu = document.querySelectorAll('.menu a');
opcionesMenu.forEach(opcion => {
  opcion.addEventListener('click', evento => {
    evento.preventDefault();                                   // no recarga la página (href="#")
    opcionesMenu.forEach(o => o.classList.remove('activo'));   // quita el azul de todas
    opcion.classList.add('activo');                            // lo pone en la que se hizo clic
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
// 6. BOTONES DE ACCIONES RÁPIDAS Y "VER TODOS"
// =========================================================
document.querySelectorAll('.btn-accion').forEach(boton => {
  boton.addEventListener('click', () => {
    mostrarAviso('Abriendo: ' + boton.dataset.accion);
  });
});

document.getElementById('btnVerTodos').addEventListener('click', () => {
  mostrarAviso('Abriendo la lista completa de pacientes');
});

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