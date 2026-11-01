import { inicializarAuth } from './modules/auth.js';
import { cargarLibros } from './modules/catalog.js';
import { ui } from './modules/ui.js';
import { api } from './modules/api.js';
import { inicializarFiltros } from './modules/filters.js';

// 1. Inicializar Login
inicializarAuth();

// 2. Inicializar Dashboard
if (window.location.pathname === '/dashboard') {
    const userStr = sessionStorage.getItem('user');
    if (!userStr) { window.location.href = '/'; } 
    else {
        const currentUser = JSON.parse(userStr);
        
        document.getElementById('userName').textContent = currentUser.nombre_completo;
        document.getElementById('userRole').textContent = currentUser.rol.toUpperCase();

        // Configurar vista según el rol
        if (currentUser.rol === 'admin') {
            document.getElementById('adminControls').style.display = 'flex';
            setInterval(checarNotificacionesAdmin, 10000);
            checarNotificacionesAdmin();
        } else {
            document.getElementById('notification-area').style.display = 'block';
            setInterval(() => checarNotificacionesAlumno(currentUser), 30000);
            checarNotificacionesAlumno(currentUser);
        }

        // Cargar catálogo e inicializar filtros
        cargarLibros(currentUser);
        inicializarFiltros();

        // Configurar Menú de Usuario
        document.getElementById('userMenuBtn').addEventListener('click', ui.toggleUserMenu);
        document.addEventListener('click', (e) => {
            const container = document.querySelector('.user-menu-container');
            if (container && !container.contains(e.target)) {
                document.getElementById('userDropdown').style.display = 'none';
            }
        });

        // Cerrar Modales con la X
        document.getElementById('closeSinopsis').addEventListener('click', () => ui.cerrarModal('modalSinopsis'));
        document.getElementById('closeSolicitar').addEventListener('click', () => ui.cerrarModal('modalSolicitar'));
        document.getElementById('closeEditarLibro').addEventListener('click', () => ui.cerrarModal('modalEditarLibro'));
        document.getElementById('closeAdmin').addEventListener('click', () => ui.cerrarModal('modalAdmin'));
        
        // Lógica de Notificaciones (Campanita)
        const notifArea = document.getElementById('notification-area');
        const closeNotif = document.getElementById('closeNotificaciones');
        if(notifArea) {
            notifArea.addEventListener('click', () => {
                ui.abrirModal('modalNotificaciones');
                document.getElementById('notifBadge').style.display = 'none'; // Ocultar el badge
            });
        }
        if(closeNotif) closeNotif.addEventListener('click', () => ui.cerrarModal('modalNotificaciones'));

        // Eventos de Envío (Solicitar Libro)
        document.getElementById('btnConfirmarPrestamo').addEventListener('click', async () => {
            const titulo = document.getElementById('solicitarLibroNombre').dataset.titulo;
            const fecha = document.getElementById('inputFechaEntrega').value;
            const res = await api.solicitarPrestamo({ titulo, id_usuario: currentUser.id_usuario, tipo_usuario: currentUser.rol, fecha_retorno: fecha });
            ui.cerrarModal('modalSolicitar');
            if(res.success) alert("Solicitud enviada. Espera aprobación.");
            else alert("Error: " + res.error);
        });

        // Evento de Edición de Libro
        document.getElementById('btnGuardarEdicion').addEventListener('click', async () => {
            const payload = {
                titulo_original: document.getElementById('editTituloOriginal').value,
                nuevo_titulo: document.getElementById('editTitulo').value,
                nuevo_autor: document.getElementById('editAutor').value,
                nueva_sinopsis: document.getElementById('editSinopsis').value,
                nueva_categoria: document.getElementById('editCategoria').value,
                nuevo_stock: parseInt(document.getElementById('editStock').value)
            };
            await api.editarLibro(payload);
            ui.cerrarModal('modalEditarLibro');
            cargarLibros(currentUser);
        });

        // Botones de Admin
        if(currentUser.rol === 'admin') {
            document.getElementById('btnVerSolicitudes').addEventListener('click', () => abrirAdminModal('solicitudes'));
            document.getElementById('btnVerDevoluciones').addEventListener('click', () => abrirAdminModal('devoluciones'));
            document.getElementById('btnAgregarLibro').addEventListener('click', () => abrirAdminModal('agregar'));
        }
    }
}

// ================= FUNCIONES DE ADMIN Y NOTIFICACIONES =================

async function checarNotificacionesAlumno(user) {
    try {
        const solicitudes = await api.getNotificaciones(user.id_usuario);
        const aprobadas = solicitudes.filter(s => s.estado === 'aprobada');
        
        if (aprobadas.length > 0) {
            document.getElementById('notifBadge').style.display = 'flex';
            const lista = document.getElementById('notificacionesLista');
            lista.innerHTML = '';
            
            aprobadas.forEach(s => {
                let alerta = s.alerta_vencimiento ? `<br><span style="color:#ef4444; font-size:12px;">¡Fecha de entrega cerca!</span>` : '';
                lista.innerHTML += `<div style="padding: 12px; margin-bottom: 10px; background: #f0fdf4; border-left: 4px solid #10b981;">
                    <strong>Aprobado:</strong> "${s.libro}"${alerta}
                </div>`;
            });
        }
    } catch(e) {}
}

async function checarNotificacionesAdmin() {
    try {
        const data = await api.getAdminCount();
        const badge = document.getElementById('adminSolicitudesBadge');
        if(data.count > 0) { badge.style.display = 'block'; badge.textContent = data.count; } 
        else { badge.style.display = 'none'; }
    } catch(e) {}
}

async function abrirAdminModal(tipo) {
    const title = document.getElementById('adminModalTitle');
    const content = document.getElementById('adminModalContent');
    content.innerHTML = '<p>Cargando...</p>';
    ui.abrirModal('modalAdmin');

    if (tipo === 'solicitudes') {
        title.textContent = 'Solicitudes Pendientes';
        const data = await api.getAdminSolicitudes();
        content.innerHTML = data.length === 0 ? '<p>No hay solicitudes.</p>' : '';
        
        data.forEach(s => {
            content.innerHTML += `
                <div class="admin-list-item">
                    <div>
                        <p><strong>${s.libro}</strong></p>
                        <p style="font-size:12px; color:#64748b;">Solicita: ${s.usuario}</p>
                        <p style="font-size:12px; color:#64748b;">Devolución: ${s.retorno}</p>
                    </div>
                    <div>
                        <button class="btn-small btn-success" onclick="window.procesarSolicitud(${s.id}, 'aceptar')">Aceptar</button>
                        <button class="btn-small btn-danger" onclick="window.procesarSolicitud(${s.id}, 'rechazar')">Rechazar</button>
                    </div>
                </div>
            `;
        });
        } else if (tipo === 'devoluciones') {
        title.textContent = 'Préstamos Activos';
        const data = await api.getAdminDevoluciones();
        content.innerHTML = data.length === 0 ? '<p>No hay libros prestados.</p>' : '';
        
        data.forEach(p => {
            const alertClass = p.alerta ? 'alerta-roja' : '';
            // Verificamos el rol para mostrar el texto correcto
            const tipoUsuario = p.rol === 'docente' ? 'Docente' : 'Alumno'; 
            
            content.innerHTML += `
                <div class="admin-list-item ${alertClass}">
                    <div>
                        <p><strong>${p.libro}</strong></p>
                        <p style="font-size:12px; color:#64748b;">${tipoUsuario}: ${p.usuario}</p>
                        <p style="font-size:12px; color:#64748b;">Devolver: ${p.fecha_entrega}</p>
                        ${p.alerta ? '<p style="font-size:12px; color:#ef4444; font-weight:bold;">¡Vence pronto!</p>' : ''}
                    </div>
                    <div>
                        <button class="btn-small btn-success" onclick="window.procesarDevolucion(${p.id})">Recibir</button>
                    </div>
                </div>
            `;
        });
    } else {
        title.textContent = 'Agregar Libro';
        content.innerHTML = `
            <input type="text" id="addTitulo" placeholder="Título" style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;">
            <input type="text" id="addAutor" placeholder="Autor" style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;">
            <input type="text" id="addCategoria" placeholder="Categoría" style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;">
            <textarea id="addSinopsis" placeholder="Sinopsis" style="width:100%; padding:10px; margin-bottom:10px; height:80px; border:1px solid #cbd5e1; border-radius:6px;"></textarea>
            <input type="number" id="addStock" placeholder="Stock" value="1" style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;">
            <button class="btn-primary" onclick="window.guardarLibro()">Guardar Libro</button>
        `;
    }
}

// Exponer funciones al objeto window para que los botones generados puedan usarlas
window.procesarSolicitud = async (id, accion) => {
    await api.procesarSolicitud(id, accion);
    abrirAdminModal('solicitudes');
    checarNotificacionesAdmin();
    const currentUser = JSON.parse(sessionStorage.getItem('user'));
    cargarLibros(currentUser);
};

window.procesarDevolucion = async (id) => {
    await api.devolverLibro(id);
    abrirAdminModal('devoluciones');
    const currentUser = JSON.parse(sessionStorage.getItem('user'));
    cargarLibros(currentUser);
};

window.guardarLibro = async () => {
    const payload = {
        titulo: document.getElementById('addTitulo').value,
        autor: document.getElementById('addAutor').value,
        categoria: document.getElementById('addCategoria').value,
        sinopsis: document.getElementById('addSinopsis').value,
        stock: parseInt(document.getElementById('addStock').value)
    };
    if(!payload.titulo || !payload.autor) return alert("Completa los campos");
    
    await api.agregarLibro(payload);
    ui.cerrarModal('modalAdmin');
    const currentUser = JSON.parse(sessionStorage.getItem('user'));
    cargarLibros(currentUser);
};