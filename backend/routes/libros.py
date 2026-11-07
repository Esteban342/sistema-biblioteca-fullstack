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
            SELECT l.id_libro, l.titulo_libro, l.autor, i.cantidad as stock, l.temas as sinopsis, l.clasificacion
            FROM libros l LEFT JOIN inventario i ON l.id_libro = i.id_libro
            ORDER BY l.titulo_libro
        """)
        libros = [{'id': r[0], 'titulo': r[1], 'autor': r[2], 'stock': r[3] or 0, 'sinopsis': r[4] or "Sin sinopsis", 'categoria': r[5] or "General"} for r in cur.fetchall()]
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