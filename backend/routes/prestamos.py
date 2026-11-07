from flask import Blueprint, jsonify, request
from database import get_db_connection
from datetime import datetime

prestamos_bp = Blueprint('prestamos', __name__)

# Ruta para que el alumno o docente pida un libro
@prestamos_bp.route('/api/solicitar-prestamo', methods=['POST'])
def solicitar_prestamo():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Revisamos que haya stock
        cur.execute("SELECT i.cantidad FROM inventario i JOIN libros l ON i.id_libro = l.id_libro WHERE l.titulo_libro = %s", (data['titulo'],))
        stock_result = cur.fetchone()
        
        if not stock_result or stock_result[0] <= 0:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Libro sin stock disponible'}), 400
        
        cur.execute("SELECT id_libro FROM libros WHERE titulo_libro = %s", (data['titulo'],))
        id_libro = cur.fetchone()[0]
        
        # Guardamos la solicitud
        cur.execute("""
            INSERT INTO solicitud_prestamo (id_usuario, id_libro, tipo_usuario, estado, fecha_retorno_estimada)
            VALUES (%s, %s, %s, 'pendiente', %s)
            RETURNING id_solicitud
        """, (data['id_usuario'], id_libro, data['tipo_usuario'], data['fecha_retorno']))
        
        id_solicitud = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Solicitud enviada', 'id_solicitud': id_solicitud})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Ruta para que el usuario vea sus solicitudes y notificaciones
@prestamos_bp.route('/api/mis-solicitudes/<int:id_usuario>', methods=['GET'])
def obtener_mis_solicitudes(id_usuario):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT sp.id_solicitud, l.titulo_libro, sp.estado, sp.fecha_solicitud, sp.fecha_retorno_estimada
            FROM solicitud_prestamo sp
            JOIN libros l ON sp.id_libro = l.id_libro
            WHERE sp.id_usuario = %s
            ORDER BY sp.fecha_solicitud DESC
        """, (id_usuario,))
        
        solicitudes = []
        hoy = datetime.now()
        for r in cur.fetchall():
            estado = r[2]
            fecha_retorno = r[4]
            alerta_vencimiento = False
            
            if estado == 'aprobada' and fecha_retorno:
                dias_restantes = (fecha_retorno - hoy).days
                if dias_restantes <= 2:
                    alerta_vencimiento = True
                    
            solicitudes.append({
                'id': r[0], 'libro': r[1], 'estado': estado, 
                'fecha': r[3].strftime('%Y-%m-%d'), 
                'alerta_vencimiento': alerta_vencimiento
            })
        
        cur.close()
        conn.close()
        return jsonify(solicitudes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para que el admin vea los prestamos activos
@prestamos_bp.route('/api/admin/prestamos-activos', methods=['GET'])
def obtener_prestamos_activos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT pa.id_prestamo, u.nombre_completo, l.titulo_libro, pa.tiempo_prestamo, pa.tiempo_devolucion, u.rol
            FROM prestamo_alumno pa JOIN usuarios u ON pa.id_usuario = u.id_usuario JOIN libros l ON pa.id_libro = l.id_libro
            WHERE pa.tiempo_devolucion > CURRENT_TIMESTAMP
            UNION
            SELECT pp.id_prestamo, u.nombre_completo, l.titulo_libro, pp.tiempo_prestamo, pp.tiempo_devolucion, u.rol
            FROM prestamo_profesor pp JOIN usuarios u ON pp.id_usuario = u.id_usuario JOIN libros l ON pp.id_libro = l.id_libro
            WHERE pp.tiempo_devolucion > CURRENT_TIMESTAMP
            ORDER BY 4 ASC
        """)
        
        hoy = datetime.now()
        prestamos = []
        for r in cur.fetchall():
            fecha_dev = r[4]
            dias_restantes = (fecha_dev - hoy).days
            alerta = dias_restantes <= 2 
            
            prestamos.append({
                'id': r[0], 
                'usuario': r[1], 
                'libro': r[2], 
                'fecha_prestamo': r[3].strftime('%Y-%m-%d'), 
                'fecha_entrega': fecha_dev.strftime('%Y-%m-%d'), 
                'alerta': alerta,
                'rol': r[5]
            })
        
        cur.close()
        conn.close()
        return jsonify(prestamos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para contar cuantas solicitudes pendientes hay
@prestamos_bp.route('/api/admin/count-solicitudes', methods=['GET'])
def count_solicitudes():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM solicitud_prestamo WHERE estado = 'pendiente'")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para aceptar o rechazar una solicitud
@prestamos_bp.route('/api/admin/procesar-solicitud', methods=['POST'])
def procesar_solicitud():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if data['accion'] == 'aceptar':
            cur.execute("SELECT id_usuario, id_libro, tipo_usuario, fecha_retorno_estimada FROM solicitud_prestamo WHERE id_solicitud = %s", (data['id_solicitud'],))
            solicitud = cur.fetchone()
            id_usuario, id_libro, tipo_usuario, fecha_retorno = solicitud
            
            cur.execute("UPDATE inventario SET cantidad = cantidad - 1 WHERE id_libro = %s", (id_libro,))
            
            tabla = 'prestamo_alumno' if tipo_usuario == 'alumno' else 'prestamo_profesor'
            cur.execute(f"""
                INSERT INTO {tabla} (id_usuario, id_libro, tipo_usuario, id_solicitud, tiempo_devolucion)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_usuario, id_libro, tipo_usuario, data['id_solicitud'], fecha_retorno))
            
            cur.execute("UPDATE solicitud_prestamo SET estado = 'aprobada', fecha_resolucion = CURRENT_TIMESTAMP WHERE id_solicitud = %s", (data['id_solicitud'],))
            
        elif data['accion'] == 'rechazar':
            cur.execute("UPDATE solicitud_prestamo SET estado = 'rechazada', fecha_resolucion = CURRENT_TIMESTAMP WHERE id_solicitud = %s", (data['id_solicitud'],))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Ruta para registrar la devolucion de un libro
@prestamos_bp.route('/api/admin/devolver', methods=['POST'])
def devolver_libro():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id_libro FROM prestamo_alumno WHERE id_prestamo = %s", (data['id_prestamo'],))
        res = cur.fetchone()
        tabla = 'prestamo_alumno'
        
        if not res:
            cur.execute("SELECT id_libro FROM prestamo_profesor WHERE id_prestamo = %s", (data['id_prestamo'],))
            res = cur.fetchone()
            tabla = 'prestamo_profesor'
            
        id_libro = res[0]
        
        cur.execute(f"DELETE FROM {tabla} WHERE id_prestamo = %s", (data['id_prestamo'],))
        cur.execute("UPDATE inventario SET cantidad = cantidad + 1 WHERE id_libro = %s", (id_libro,))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500