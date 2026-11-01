-- Borrar las tablas si ya existen (para evitar errores si lo corres varias veces)
DROP TABLE IF EXISTS Prestamo_Profesor CASCADE;
DROP TABLE IF EXISTS Prestamo_Alumno CASCADE;
DROP TABLE IF EXISTS Inventario CASCADE;
DROP TABLE IF EXISTS Libros CASCADE;

-- 1. Crear tabla de Libros
CREATE TABLE Libros (
    id_libro SERIAL PRIMARY KEY,
    Clasificacion VARCHAR(100),
    Temas_totales INT,
    Titulo_libro VARCHAR(255),
    Autor VARCHAR(150),
    Editorial VARCHAR(150),
    Edicion INT,
    Año_Edicion INT,
    Temas VARCHAR(255),
    CD VARCHAR(50),
    Libros_Relacionados VARCHAR(255),
    ISBN BIGINT,
    Fuente_Recurso VARCHAR(255)
);

-- 2. Crear tabla de Inventario
CREATE TABLE Inventario (
    id SERIAL PRIMARY KEY,
    cantidad INT,
    estado VARCHAR(50),
    disponibilidad VARCHAR(20),
    id_libro INT NOT NULL,
    FOREIGN KEY (id_libro) REFERENCES Libros(id_libro) ON DELETE CASCADE
);

-- 3. Crear tabla de Préstamo Alumno
CREATE TABLE Prestamo_Alumno (
    id_Prestamo SERIAL PRIMARY KEY,
    matricula VARCHAR(15),  
    id_libro INT REFERENCES Libros(id_libro) ON DELETE CASCADE,
    tiempo_prestamo TIMESTAMP,
    tiempo_devolucion TIMESTAMP
);

-- 4. Crear tabla de Préstamo Profesor
CREATE TABLE Prestamo_Profesor (
    id_Prestamo SERIAL PRIMARY KEY,
    matricula_p VARCHAR(15), 
    id_libro INT REFERENCES Libros(id_libro) ON DELETE CASCADE,
    tiempo_prestamo TIMESTAMP,
    tiempo_devolucion TIMESTAMP
);

-- ==========================================
-- INSERTAR DATOS DE PRUEBA (12 LIBROS)
-- ==========================================

INSERT INTO Libros (Clasificacion, Temas_totales, Titulo_libro, Autor, Editorial, Edicion, Año_Edicion, Temas, ISBN, Fuente_Recurso) VALUES 
('Programación', 10, 'Algoritmos y programación en pseudocódigo', 'Diego Fernando Duque Strock', 'McGraw-Hill', 1, 2020, 'Este libro aborda los fundamentos de la lógica de programación, el diseño de algoritmos y su implementación utilizando pseudocódigo.', 9781234567890, 'Físico'),
('Bases de Datos', 8, 'Bases de Datos Relacionales y SQL', 'Ana Belén Cruz', 'Pearson', 2, 2021, 'Guía completa sobre el modelado de datos, la teoría relacional y el lenguaje SQL. Cubre desde consultas básicas hasta procedimientos almacenados.', 9780987654321, 'Físico'),
('Desarrollo Web', 12, 'Introducción al Desarrollo Web Frontend', 'Carlos Manuel López', 'Alfaomega', 1, 2022, 'Un recorrido por HTML, CSS y JavaScript para construir interfaces de usuario interactivas y responsivas. Incluye ejercicios prácticos.', 9781122334455, 'Digital'),
('Ingeniería de Software', 6, 'Ingeniería de Software Ágil', 'Luisa Fernanda Soto', 'Addison-Wesley', 3, 2019, 'Exploración de metodologías ágiles como Scrum y Kanban. Se centra en la gestión de requisitos, la planificación de sprints y las mejores prácticas.', 9785566778899, 'Físico'),
('Estructuras de Datos', 15, 'Estructuras de Datos Avanzadas', 'Diego Fernando Duque Strock', 'McGraw-Hill', 2, 2021, 'Análisis profundo de estructuras complejas como árboles B, grafos y tablas hash. Esencial para la optimización de algoritmos.', 9789988776655, 'Físico'),
('Redes', 9, 'Redes de Computadoras y Protocolos TCP/IP', 'Miguel Ángel Ramírez', 'Prentice Hall', 4, 2018, 'Estudio del modelo OSI y la suite TCP/IP. Detalla el funcionamiento de enrutadores, subredes y los protocolos de capa de transporte.', 9784433221100, 'Físico'),
('Seguridad', 7, 'Ciberseguridad y Ethical Hacking', 'Valentina Rojas', 'Ra-Ma', 1, 2023, 'Introducción a las técnicas de hacking ético, la prevención de intrusiones y la defensa contra amenazas comunes en sistemas y redes.', 9783322110099, 'Digital'),
('Matemáticas', 5, 'Matemáticas Discretas para Programación', 'Jorge Iván Castro', 'Cengage', 2, 2020, 'Temas como lógica proposicional, teoría de conjuntos, funciones, relaciones y conteo, fundamentales para la algoritmia.', 9782211009988, 'Físico'),
('Desarrollo Móvil', 11, 'Desarrollo de Aplicaciones Móviles con Kotlin', 'Camilo Andrés Osorio', 'O\'Reilly', 1, 2022, 'Creación de apps nativas para Android usando Kotlin. Cubre el ciclo de vida de la actividad, manejo de vistas y bases de datos locales.', 9781100998877, 'Digital'),
('Inteligencia Artificial', 14, 'Fundamentos de Inteligencia Artificial', 'Laura Marcela Pérez', 'Pearson', 3, 2021, 'Conceptos clave de IA, aprendizaje automático (Machine Learning), redes neuronales y algoritmos de búsqueda heurística.', 9780099887766, 'Físico'),
('Programación', 8, 'Programación Orientada a Objetos en Java', 'Ricardo Jiménez', 'Alfaomega', 5, 2019, 'Dominio de los cuatro pilares de la POO: Encapsulamiento, Herencia, Polimorfismo y Abstracción, con ejemplos en Java.', 9788877665544, 'Físico'),
('Sistemas Operativos', 10, 'Sistemas Operativos Modernos', 'Mónica Patricia Vélez', 'Pearson', 4, 2017, 'Estudio del manejo de procesos, la gestión de memoria, sistemas de archivos y la concurrencia en sistemas operativos actuales.', 9787766554433, 'Físico');

-- Insertar el stock de los libros en la tabla Inventario
-- (Los IDs del 1 al 12 coinciden con el orden en que se insertaron los libros)
INSERT INTO Inventario (cantidad, estado, disponibilidad, id_libro) VALUES 
(5, 'Bueno', 'Disponible', 1),
(3, 'Bueno', 'Disponible', 2),
(8, 'Nuevo', 'Disponible', 3),
(2, 'Regular', 'Disponible', 4),
(6, 'Nuevo', 'Disponible', 5),
(4, 'Bueno', 'Disponible', 6),
(5, 'Bueno', 'Disponible', 7),
(7, 'Nuevo', 'Disponible', 8),
(9, 'Nuevo', 'Disponible', 9),
(1, 'Regular', 'Disponible', 10),
(4, 'Bueno', 'Disponible', 11),
(3, 'Bueno', 'Disponible', 12);