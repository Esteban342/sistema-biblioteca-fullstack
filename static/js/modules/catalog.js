import { api } from './api.js';
import { ui } from './ui.js';
import { llenarCategorias } from './filters.js';

export async function cargarLibros(user) {
    try {
        const libros = await api.getLibros();
        const grid = document.getElementById('booksGrid');
        
        grid.innerHTML = '';

        libros.forEach(libro => {
            const hasStock = libro.stock > 0;
            const stockClass = hasStock ? 'stock-ok' : 'stock-no';
            const stockText = hasStock ? `Stock: ${libro.stock}` : 'Sin Stock';
            
            const card = document.createElement('div');
            card.className = 'book-card';
            card.dataset.categoria = libro.categoria;
            
            let actionBtns = '';
            if (user.rol === 'admin') {
                actionBtns = `<button class="btn-action btn-solid btn-editar" data-titulo="${libro.titulo}" data-autor="${libro.autor}" data-sinopsis="${libro.sinopsis}" data-categoria="${libro.categoria}" data-stock="${libro.stock}">Editar Libro</button>`;
            } else {
                actionBtns = `
                    <button class="btn-action btn-outline btn-ver-sinopsis" data-titulo="${libro.titulo}" data-sinopsis="${libro.sinopsis}">Sinopsis</button>
                    <button class="btn-action btn-solid btn-solicitar" ${!hasStock ? 'disabled' : ''} data-titulo="${libro.titulo}">${hasStock ? 'Solicitar' : 'Agotado'}</button>
                `;
            }

            card.innerHTML = `
                <div>
                    <div class="book-title">${libro.titulo}</div>
                    <div class="book-author">${libro.autor}</div>
                    <div style="font-size:11px; color:#94a3b8; margin-bottom:5px;">${libro.categoria}</div>
                    <div class="book-stock ${stockClass}">${stockText}</div>
                </div>
                <div class="card-actions">${actionBtns}</div>
            `;
            grid.appendChild(card);
        });

        // Llenar el filtro de categorías
        llenarCategorias(libros);

        asignarEventosBotones(user);

    } catch (error) { 
        console.error("Error al cargar libros:", error); 
    }
}

function asignarEventosBotones(user) {
    document.querySelectorAll('.btn-ver-sinopsis').forEach(btn => {
        btn.addEventListener('click', (e) => {
            ui.verSinopsis(e.target.dataset.titulo, e.target.dataset.sinopsis);
        });
    });

    document.querySelectorAll('.btn-solicitar').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const titulo = e.target.dataset.titulo;
            document.getElementById('solicitarLibroNombre').textContent = titulo;
            document.getElementById('solicitarLibroNombre').dataset.titulo = titulo;
            
            const hoy = new Date();
            const proxSemana = new Date();
            proxSemana.setDate(hoy.getDate() + 7);
            
            document.getElementById('solicitarFechaHoy').textContent = hoy.toLocaleDateString('es-ES');
            document.getElementById('inputFechaEntrega').value = proxSemana.toISOString().split('T')[0];
            ui.abrirModal('modalSolicitar');
        });
    });

    document.querySelectorAll('.btn-editar').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.getElementById('editTituloOriginal').value = e.target.dataset.titulo;
            document.getElementById('editTitulo').value = e.target.dataset.titulo;
            document.getElementById('editAutor').value = e.target.dataset.autor;
            document.getElementById('editSinopsis').value = e.target.dataset.sinopsis;
            document.getElementById('editCategoria').value = e.target.dataset.categoria;
            document.getElementById('editStock').value = e.target.dataset.stock;
            ui.abrirModal('modalEditarLibro');
        });
    });
}