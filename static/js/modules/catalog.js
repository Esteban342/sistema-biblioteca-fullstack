import { api } from './api.js';
import { ui } from './ui.js';
import { llenarCategorias } from './filters.js';

export async function cargarLibros(user) {
    try {
        const libros = await api.getLibros();
        const grid = document.getElementById('booksGrid');
        
        if (!Array.isArray(libros)) return;
        grid.innerHTML = '';

        libros.forEach(libro => {
            const hasStock = libro.stock > 0;
            const stockClass = hasStock ? 'stock-ok' : 'stock-no';
            const stockText = hasStock ? `Stock: ${libro.stock}` : 'Sin Stock';
            const imagen = libro.imagen_url || 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80';
            
            const rating = libro.rating || 0;
            const estrellasStr = '★'.repeat(Math.round(rating)) + '☆'.repeat(5 - Math.round(rating));
            
            const card = document.createElement('div');
            card.className = 'book-card';
            card.style.cursor = 'pointer';
            card.dataset.categoria = libro.categoria;
            
            card.addEventListener('click', () => {
                window.location.href = `/libro/${libro.id}`;
            });

            let actionBtns = '';
            if (user.rol === 'admin') {
                // Solo el admin ve el botón de editar directo en la tarjeta
                 actionBtns = `<button class="btn-action btn-solid btn-editar" onclick="event.stopPropagation();" data-id="${libro.id}" data-titulo="${libro.titulo}" data-autor="${libro.autor}" data-sinopsis="${libro.sinopsis}" data-categoria="${libro.categoria}" data-stock="${libro.stock}" data-imagen="${libro.imagen_url || ''}">Editar</button>`;
            } else {
                // El alumno solo ve un texto que lo invita a entrar
                actionBtns = `<div style="text-align: center; color: #3b82f6; font-weight: 600; font-size: 14px; margin-top: 10px;">Ver detalles <i class="fa-solid fa-arrow-right"></i></div>`;
            }

            card.innerHTML = `
                <div>
                    <div style="background-image: url('${imagen}'); height: 240px; background-size: contain; background-repeat: no-repeat; background-position: center; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); background-color: #f8fafc;"></div>                    <div class="book-title">${libro.titulo}</div>
                    <div class="book-author">${libro.autor}</div>
                    <div style="color: #f59e0b; font-size: 16px; margin-bottom: 8px;">
                        ${estrellasStr} <span style="color: #64748b; font-size: 12px; margin-left: 4px;">(${rating})</span>
                    </div>
                    <div style="font-size:11px; color:#94a3b8; margin-bottom:5px;">${libro.categoria}</div>
                    <div class="book-stock ${stockClass}">${stockText}</div>
                </div>
                <div class="card-actions">${actionBtns}</div>
            `;
            grid.appendChild(card);
        });

        llenarCategorias(libros);
        asignarEventosBotones();

    } catch (error) { 
        console.error("Error al cargar libros:", error); 
    }
}

function asignarEventosBotones() {
    document.querySelectorAll('.btn-editar').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Pasamos los datos al modal
            document.getElementById('editTituloOriginal').value = e.target.dataset.titulo;
            document.getElementById('editTituloOriginal').dataset.id = e.target.dataset.id; 
            document.getElementById('editTitulo').value = e.target.dataset.titulo;
            document.getElementById('editAutor').value = e.target.dataset.autor;
            document.getElementById('editSinopsis').value = e.target.dataset.sinopsis;
            document.getElementById('editCategoria').value = e.target.dataset.categoria;
            document.getElementById('editStock').value = e.target.dataset.stock;
            // Nuevo campo de imagen
            document.getElementById('editImagen').value = e.target.dataset.imagen;
            ui.abrirModal('modalEditarLibro');
        });
    });
}