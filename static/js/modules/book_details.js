import { api } from './api.js';

export async function cargarDetalleLibro(id_libro) {
    const container = document.getElementById('detailsContainer');
    try {
        const libro = await api.getLibroDetalle(id_libro);
        
        if (libro.error) {
            container.innerHTML = `<p style="color:red; text-align:center;">Error: ${libro.error}</p>`;
            return;
        }

        const imagen = libro.imagen_url || 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80';
        const hasStock = libro.stock > 0;
        
        // Dibujar la información del libro y las reseñas
        container.innerHTML = `
            <div class="book-info-panel">
                <img src="${imagen}" alt="${libro.titulo}">
                <h1>${libro.titulo}</h1>
                <div class="author">Por: ${libro.autor} | Categoría: ${libro.categoria}</div>
                <div class="synopsis">${libro.sinopsis}</div>
                <div style="font-size: 18px; font-weight: bold; margin-bottom: 20px;" class="${hasStock ? 'stock-ok' : 'stock-no'}">
                    ${hasStock ? `Disponible (${libro.stock} en stock)` : 'Agotado temporalmente'}
                </div>
                <button class="btn-primary" ${!hasStock ? 'disabled' : ''} onclick="alert('Para solicitar el préstamo, regresa al catálogo.')">Solicitar Préstamo</button>
            </div>
            
            <div class="reviews-panel">
                <h2>Reseñas y Calificaciones</h2>
                <div id="reviewsList">
                    ${libro.resenas.length === 0 ? '<p>No hay reseñas todavía. ¡Sé el primero en opinar!</p>' : ''}
                </div>
                
                <div class="add-review-form">
                    <h3>Deja tu reseña</h3>
                    <div class="star-rating" id="starRating">
                        <i class="fa-solid fa-star" data-val="1"></i>
                        <i class="fa-solid fa-star" data-val="2"></i>
                        <i class="fa-solid fa-star" data-val="3"></i>
                        <i class="fa-solid fa-star" data-val="4"></i>
                        <i class="fa-solid fa-star" data-val="5"></i>
                    </div>
                    <textarea id="reviewComment" placeholder="¿Qué te pareció este libro?"></textarea>
                    <button class="btn-primary" id="btnSubmitReview">Enviar Reseña</button>
                </div>
            </div>
        `;

        // Llenar las reseñas existentes
        const reviewsList = document.getElementById('reviewsList');
        if (libro.resenas.length === 0) {
            reviewsList.innerHTML = '<p style="color:#64748b;">No hay reseñas todavía. ¡Sé el primero en opinar!</p>';
        } else {
            reviewsList.innerHTML = '';
            libro.resenas.forEach(resena => {
                const estrellas = '★'.repeat(resena.calificacion) + '☆'.repeat(5 - resena.calificacion);
                reviewsList.innerHTML += `
                    <div class="review-item">
                        <div class="review-header">
                            <span>${resena.usuario}</span>
                            <span class="stars">${estrellas}</span>
                        </div>
                        <div class="comment">${resena.comentario}</div>
                        <div style="font-size: 11px; color: #94a3b8; margin-top: 5px;">${resena.fecha}</div>
                    </div>
                `;
            });
        }

        // Lógica para seleccionar estrellas
        let selectedRating = 0;
        const stars = document.querySelectorAll('#starRating i');
        stars.forEach(star => {
            star.addEventListener('click', (e) => {
                selectedRating = parseInt(e.target.dataset.val);
                stars.forEach(s => {
                    if (parseInt(s.dataset.val) <= selectedRating) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });
            });
        });

        // Enviar la reseña
        document.getElementById('btnSubmitReview').addEventListener('click', async () => {
            const comentario = document.getElementById('reviewComment').value;
            const userStr = sessionStorage.getItem('user');
            
            if (!userStr) return alert("Debes iniciar sesión.");
            if (selectedRating === 0) return alert("Por favor, selecciona una calificación con las estrellas.");
            if (!comentario.trim()) return alert("Por favor, escribe un comentario.");

            const currentUser = JSON.parse(userStr);
            
            const res = await api.crearResena({
                id_libro: libro.id,
                id_usuario: currentUser.id_usuario,
                calificacion: selectedRating,
                comentario: comentario
            });

            if (res.success) {
                alert("¡Reseña guardada con éxito!");
                cargarDetalleLibro(id_libro); // Recargar la página
            } else {
                alert("Error: " + res.error);
            }
        });

    } catch (error) {
        console.error(error);
        container.innerHTML = `<p style="color:red; text-align:center;">Error de conexión.</p>`;
    }
}