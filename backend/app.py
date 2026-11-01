from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)

# Datos para entrar a la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'Biblioteca'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Funcion para conectar a la base de datos
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Rutas para mostrar las paginas web
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Ruta para iniciar sesion
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_usuario, rol, nombre_completo FROM usuarios WHERE username = %s AND password = %s", (data['username'], data['password']))
        res = cur.fetchone()
        cur.close()
        conn.close()
        
        if res:
            return jsonify({'success': True, 'id_usuario': res[0], 'rol': res[1], 'username': data['username'], 'nombre_completo': res[2]})
        return jsonify({'success': False, 'error': 'Credenciales incorrectas'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Ruta para obtener todos los libros
@app.route('/api/libros', methods=['GET'])
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

# Ruta para que el alumno o docente pida un libro
@app.route('/api/solicitar-prestamo', methods=['POST'])
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
@app.route('/api/mis-solicitudes/<int:id_usuario>', methods=['GET'])
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
            
            # Si ya esta aprobada, vemos cuantos dias faltan
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

# Ruta para que el admin vea los prestamos activos (libros que no se han devuelto)
@app.route('/api/admin/prestamos-activos', methods=['GET'])
def obtener_prestamos_activos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Aqui unimos las tablas para saber el rol y la fecha
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
            alerta = dias_restantes <= 2 # Si faltan 2 dias o menos, se marca alerta
            
            prestamos.append({
                'id': r[0], 
                'usuario': r[1], 
                'libro': r[2], 
                'fecha_prestamo': r[3].strftime('%Y-%m-%d'), 
                'fecha_entrega': fecha_dev.strftime('%Y-%m-%d'), 
                'alerta': alerta,
                'rol': r[5] # Mandamos el rol para que el JS sepa si es Alumno o Docente
            })
        
        cur.close()
        conn.close()
        return jsonify(prestamos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para contar cuantas solicitudes pendientes hay
@app.route('/api/admin/count-solicitudes', methods=['GET'])
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
@app.route('/api/admin/procesar-solicitud', methods=['POST'])
def procesar_solicitud():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if data['accion'] == 'aceptar':
            cur.execute("SELECT id_usuario, id_libro, tipo_usuario, fecha_retorno_estimada FROM solicitud_prestamo WHERE id_solicitud = %s", (data['id_solicitud'],))
            solicitud = cur.fetchone()
            id_usuario, id_libro, tipo_usuario, fecha_retorno = solicitud
            
            # Le bajamos el stock al libro
            cur.execute("UPDATE inventario SET cantidad = cantidad - 1 WHERE id_libro = %s", (id_libro,))
            
            # Lo guardamos en la tabla que toca
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
@app.route('/api/admin/devolver', methods=['POST'])
def devolver_libro():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Vemos si el prestamo era de alumno o de profesor
        cur.execute("SELECT id_libro FROM prestamo_alumno WHERE id_prestamo = %s", (data['id_prestamo'],))
        res = cur.fetchone()
        tabla = 'prestamo_alumno'
        
        if not res:
            cur.execute("SELECT id_libro FROM prestamo_profesor WHERE id_prestamo = %s", (data['id_prestamo'],))
            res = cur.fetchone()
            tabla = 'prestamo_profesor'
            
        id_libro = res[0]
        
        # Borramos el prestamo y le devolvemos el stock al libro
        cur.execute(f"DELETE FROM {tabla} WHERE id_prestamo = %s", (data['id_prestamo'],))
        cur.execute("UPDATE inventario SET cantidad = cantidad + 1 WHERE id_libro = %s", (id_libro,))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Ruta para editar un libro
@app.route('/api/admin/editar-libro', methods=['POST'])
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

# Ruta para agregar un nuevo libro
@app.route('/api/admin/agregar-libro', methods=['POST'])
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

# Arrancamos el servidor
if __name__ == '__main__':
    app.run(debug=True, port=5000)