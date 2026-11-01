const API_URL = 'http://localhost:5000/api';

export const api = {
    login: async (username, password) => {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password })
        });
        return await res.json();
    },
    getLibros: async () => {
        const res = await fetch(`${API_URL}/libros`);
        return await res.json();
    },
    solicitarPrestamo: async (data) => {
        const res = await fetch(`${API_URL}/solicitar-prestamo`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        return await res.json();
    },
    getNotificaciones: async (id_usuario) => {
        const res = await fetch(`${API_URL}/mis-solicitudes/${id_usuario}`);
        return await res.json();
    },
    getAdminCount: async () => {
        const res = await fetch(`${API_URL}/admin/count-solicitudes`);
        return await res.json();
    },
    getAdminSolicitudes: async () => {
        const res = await fetch(`${API_URL}/admin/solicitudes`);
        return await res.json();
    },
    getAdminDevoluciones: async () => {
        const res = await fetch(`${API_URL}/admin/prestamos-activos`);
        return await res.json();
    },
    procesarSolicitud: async (id, accion) => {
        const res = await fetch(`${API_URL}/admin/procesar-solicitud`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id_solicitud: id, accion })
        });
        return await res.json();
    },
    devolverLibro: async (id_prestamo) => {
        const res = await fetch(`${API_URL}/admin/devolver`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id_prestamo })
        });
        return await res.json();
    },
    agregarLibro: async (data) => {
        const res = await fetch(`${API_URL}/admin/agregar-libro`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        return await res.json();
    },
    editarLibro: async (data) => {
        const res = await fetch(`${API_URL}/admin/editar-libro`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        return await res.json();
    }
};