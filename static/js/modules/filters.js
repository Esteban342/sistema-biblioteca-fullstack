// Lógica para el buscador y los filtros avanzados
export function inicializarFiltros() {
    const searchInput = document.getElementById('searchInput');
    const filterCategory = document.getElementById('filterCategory');
    const btnFiltros = document.getElementById('btnAdvancedSearch');
    const panelFiltros = document.getElementById('filterPanel');
    const btnApply = document.getElementById('btnApplyFilters');
    const btnClear = document.getElementById('btnClearFilters');

    if (!searchInput || !btnFiltros) return;

    // Abrir/Cerrar panel de filtros
    btnFiltros.addEventListener('click', (e) => {
        e.stopPropagation();
        panelFiltros.classList.toggle('active');
    });

    // Cerrar panel al hacer clic fuera
    document.addEventListener('click', (e) => {
        if (panelFiltros && !panelFiltros.contains(e.target) && e.target !== btnFiltros) {
            panelFiltros.classList.remove('active');
        }
    });

    // Función central que filtra las tarjetas en pantalla
    const aplicarFiltros = () => {
        const query = searchInput.value.toLowerCase();
        const cat = filterCategory ? filterCategory.value : 'all';
        
        document.querySelectorAll('.book-card').forEach(card => {
            const title = card.querySelector('.book-title').textContent.toLowerCase();
            const author = card.querySelector('.book-author').textContent.toLowerCase();
            const categoria = card.dataset.categoria || "";
            
            // Comprobar si coincide con la barra de búsqueda
            const matchesQuery = title.includes(query) || author.includes(query);
            // Comprobar si coincide con la categoría
            const matchesCat = cat === "all" || categoria === cat;
            
            card.style.display = (matchesQuery && matchesCat) ? 'flex' : 'none';
        });
    };

    // Escuchar cuando se escribe o se cambia la categoría
    searchInput.addEventListener('input', aplicarFiltros);
    if (filterCategory) filterCategory.addEventListener('change', aplicarFiltros);

    // Botones del panel
    if (btnApply) {
        btnApply.addEventListener('click', () => {
            aplicarFiltros();
            panelFiltros.classList.remove('active');
        });
    }

    if (btnClear) {
        btnClear.addEventListener('click', () => {
            searchInput.value = '';
            if(filterCategory) filterCategory.value = 'all';
            aplicarFiltros();
        });
    }
}

// Función para llenar el select con las categorías de la BD
export function llenarCategorias(libros) {
    const filterCategory = document.getElementById('filterCategory');
    if (!filterCategory || filterCategory.options.length > 1) return;
    
    const categoriasUnicas = new Set();
    libros.forEach(libro => categoriasUnicas.add(libro.categoria));

    categoriasUnicas.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat; opt.textContent = cat;
        filterCategory.appendChild(opt);
    });
}