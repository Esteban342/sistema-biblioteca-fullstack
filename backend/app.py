from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv
from routes.libros import libros_bp
from routes.auth import auth_bp
from database import get_db_connection
from routes.prestamos import prestamos_bp

load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(libros_bp)
app.register_blueprint(prestamos_bp)
# Rutas para mostrar las paginas web
@app.route('/')
def index():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/libro/<int:id_libro>')
def libro_detalle(id_libro):
    return render_template('book_details.html', id_libro=id_libro)

if __name__ == '__main__':
    app.run(debug=True, port=5000)