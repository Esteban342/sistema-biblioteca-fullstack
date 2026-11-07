from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash
from database import get_db_connection

# Creamos el Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT id_usuario, rol, nombre_completo, password FROM usuarios WHERE username = %s", (data['username'],))
        res = cur.fetchone(); cur.close(); conn.close()
        
        if res:
            if check_password_hash(res[3], data['password']):
                return jsonify({'success': True, 'id_usuario': res[0], 'rol': res[1], 'username': data['username'], 'nombre_completo': res[2]})
            else:
                return jsonify({'success': False, 'error': 'Contraseña incorrecta'})
        
        return jsonify({'success': False, 'error': 'Usuario no encontrado'})
    except Exception as e: 
        return jsonify({'success': False, 'error': str(e)}), 500