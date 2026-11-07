from flask import Blueprint, jsonify, request
from database import get_db_connection

libros_bp = Blueprint('libros', __name__)

# 1. Obtener todos los libros (Catálogo)
@libros_bp.route('/api/libros', methods=['GET'])
def obtener_libros():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT l.id_libro, l.titulo_libro, l.autor, i.cantidad as stock, 
                   l.temas as sinopsis, l.clasificacion, l.imagen_url,
                   COALESCE(AVG(r.calificacion), 0) as promedio_calificacion
            FROM libros l 
            LEFT JOIN inventario i ON l.id_libro = i.id_libro
            LEFT JOIN resenas r ON l.id_libro = r.id_libro
            GROUP BY l.id_libro, i.cantidad
            ORDER BY l.titulo_libro
        """)
        
        libros = []
        for r in cur.fetchall():
            libros.append({
                'id': r[0], 
                'titulo': r[1], 
                'autor': r[2], 
                'stock': r[3] or 0, 
                'sinopsis': r[4] or "Sin sinopsis", 
                'categoria': r[5] or "General",
                'imagen_url': r[6],
                'rating': round(float(r[7]), 1) # Promedio redondeado a 1 decimal
            })
            
        cur.close()
        conn.close()
        return jsonify(libros)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Agregar un nuevo libro (Admin)
@libros_bp.route('/api/admin/agregar-libro', methods=['POST'])
def agregar_libro():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("INSERT INTO libros (titulo_libro, autor, temas, clasificacion) VALUES (%s, %s, %s, %s) RETURNING id_libro", (data['titulo'], data['autor'], data['sinopsis'], data['categoria']))
        id_libro = cur.fetchone()[0]
        cur.execute("INSERT INTO inventario (cantidad, id_libro) VALUES (%s, %s)", (data['stock'], id_libro))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 3. Editar un libro (Admin)
@libros_bp.route('/api/admin/editar-libro', methods=['POST'])
def editar_libro():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE libros SET titulo_libro = %s, autor = %s, temas = %s, clasificacion = %s
            WHERE id_libro = (SELECT id_libro FROM libros WHERE titulo_libro = %s)
        """, (data['nuevo_titulo'], data['nuevo_autor'], data['nueva_sinopsis'], data['nueva_categoria'], data['titulo_original']))
        
        cur.execute("""
            UPDATE inventario SET cantidad = %s 
            WHERE id_libro = (SELECT id_libro FROM libros WHERE titulo_libro = %s)
        """, (data['nuevo_stock'], data['nuevo_titulo']))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
# 4. Obtener un solo libro con todas sus reseñas
@libros_bp.route('/api/libros/<int:id_libro>', methods=['GET'])
def obtener_libro_detalle(id_libro):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Datos del libro
        cur.execute("""
            SELECT l.id_libro, l.titulo_libro, l.autor, l.temas, l.clasificacion, l.imagen_url, i.cantidad
            FROM libros l 
            LEFT JOIN inventario i ON l.id_libro = i.id_libro
            WHERE l.id_libro = %s
        """, (id_libro,))
        libro_data = cur.fetchone()
        
        if not libro_data:
            return jsonify({'error': 'Libro no encontrado'}), 404
            
        # Reseñas del libro (unidas con el nombre del usuario)
        cur.execute("""
            SELECT r.calificacion, r.comentario, r.fecha, u.nombre_completo
            FROM resenas r
            JOIN usuarios u ON r.id_usuario = u.id_usuario
            WHERE r.id_libro = %s
            ORDER BY r.fecha DESC
        """, (id_libro,))
        
        resenas = []
        suma_calificaciones = 0
        for r in cur.fetchall():
            resenas.append({
                'calificacion': r[0],
                'comentario': r[1],
                'fecha': r[2].strftime('%Y-%m-%d'),
                'usuario': r[3]
            })
            suma_calificaciones += r[0]
            
        promedio = suma_calificaciones / len(resenas) if resenas else 0

        libro = {
            'id': libro_data[0],
            'titulo': libro_data[1],
            'autor': libro_data[2],
            'sinopsis': libro_data[3] or "Sin sinopsis",
            'categoria': libro_data[4] or "General",
            'imagen_url': libro_data[5],
            'stock': libro_data[6] or 0,
            'rating': round(float(promedio), 1),
            'resenas': resenas
        }
        
        cur.close()
        conn.close()
        return jsonify(libro)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 5. Guardar una nueva reseña
@libros_bp.route('/api/resenas', methods=['POST'])
def agregar_resena():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO resenas (id_libro, id_usuario, calificacion, comentario)
            VALUES (%s, %s, %s, %s)
        """, (data['id_libro'], data['id_usuario'], data['calificacion'], data['comentario']))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Reseña guardada'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500