export const ui = {
    cerrarModal: (id) => {
        document.getElementById(id).style.display = 'none';
    },
    abrirModal: (id) => {
        document.getElementById(id).style.display = 'flex';
    },
    verSinopsis: (titulo, sinopsis) => {
        document.getElementById('sinopsisTitle').textContent = titulo;
        document.getElementById('sinopsisText').textContent = sinopsis;
        ui.abrirModal('modalSinopsis');
    },
    toggleUserMenu: () => {
        const dropdown = document.getElementById('userDropdown');
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    },
    alertaNotificacion: (mensaje, tipo = 'success') => {
        // Aquí podrías usar Toastify o un toast personalizado en el futuro
        alert(mensaje); 
    }
};