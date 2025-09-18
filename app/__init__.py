from flask import Flask, jsonify, render_template, redirect, url_for, request, flash
from flask_cors import CORS
from app.configuracion import Config
from app.base_datos import probar_conexion, obtener_coleccion_gastos
from app.modelos.gasto import Gasto
from bson import ObjectId
from datetime import datetime

def crear_app():
    app = Flask(__name__)
    print("Creando aplicacion Flask")
    app.config.from_object(Config)
    print("Configuracion cargada")
    CORS(app, origins=app.config['CORS_ORIGINS'])
    print("CORS habilitado")
    if probar_conexion():
        print("Conexion a MongoDB exitosa")
    else:
        print("Advertencia: No se pudo conectar a MongoDB")
    from app.rutas.gastos import gastos_bp
    app.register_blueprint(gastos_bp, url_prefix='/api')
    print("📋 Rutas de gastos registradas")

    @app.route('/')
    def index():
        coleccion = obtener_coleccion_gastos()
        gastos = []
        if coleccion is not None:
            cursor = coleccion.find().sort('fecha', -1)
            for gasto in cursor:
                gastos.append(Gasto.formatear_para_respuesta(gasto))
        return render_template('index.html', gastos=gastos)

    @app.route('/nuevo', methods=['GET', 'POST'])
    def nuevo_gasto():
        categorias = Config.CATEGORIAS_PERMITIDAS
        if request.method == 'POST':
            descripcion = request.form.get('descripcion')
            monto = request.form.get('monto')
            fecha = request.form.get('fecha')
            if not fecha or fecha.strip() == '':
                fecha = datetime.now().strftime('%d-%m-%Y')
            categoria = request.form.get('categoria')
            origen = request.form.get('origen')
            if not descripcion or not monto or not categoria or not origen:
                flash('Todos los campos son obligatorios', 'danger')
                return redirect(url_for('nuevo_gasto'))
            if categoria not in categorias:
                flash('Categoría inválida', 'danger')
                return redirect(url_for('nuevo_gasto'))
            try:
                gasto = {
                    'descripcion': descripcion,
                    'monto': float(monto),
                    'categoria': categoria,
                    'origen': origen,
                    'fecha': fecha if fecha else None
                }
                coleccion = obtener_coleccion_gastos()
                if coleccion is not None:
                    coleccion.insert_one(gasto)
                flash('Gasto agregado exitosamente', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('nuevo_gasto'))
        return render_template('nuevo.html', categorias=categorias)

    @app.route('/editar/<gasto_id>', methods=['GET', 'POST'])
    def editar_gasto(gasto_id):
        categorias = Config.CATEGORIAS_PERMITIDAS
        coleccion = obtener_coleccion_gastos()
        gasto = None
        if coleccion is not None:
            gasto_db = coleccion.find_one({'_id': ObjectId(gasto_id)})
            if gasto_db:
                gasto = Gasto.formatear_para_respuesta(gasto_db)
        if request.method == 'POST':
            descripcion = request.form.get('descripcion')
            monto = request.form.get('monto')
            fecha = request.form.get('fecha')
            categoria = request.form.get('categoria')
            origen = request.form.get('origen')
            if not descripcion or not monto or not categoria or not origen:
                flash('Todos los campos son obligatorios', 'danger')
                return redirect(url_for('editar_gasto', gasto_id=gasto_id))
            if categoria not in categorias:
                flash('Categoría inválida', 'danger')
                return redirect(url_for('editar_gasto', gasto_id=gasto_id))
            try:
                datos_actualizados = {
                    'descripcion': descripcion,
                    'monto': float(monto),
                    'categoria': categoria,
                    'origen': origen,
                    'fecha': fecha if fecha else None,
                    'fecha_actualizacion': datetime.now()
                }
                coleccion.update_one({'_id': ObjectId(gasto_id)}, {'$set': datos_actualizados})
                flash('Gasto editado exitosamente', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('editar_gasto', gasto_id=gasto_id))
        return render_template('nuevo.html', categorias=categorias, gasto=gasto, editar=True)

    @app.route('/borrar/<gasto_id>', methods=['POST'])
    def borrar_gasto(gasto_id):
        coleccion = obtener_coleccion_gastos()
        if coleccion is not None:
            resultado = coleccion.delete_one({'_id': ObjectId(gasto_id)})
            if resultado.deleted_count:
                flash('Gasto eliminado exitosamente', 'success')
            else:
                flash('No se pudo eliminar el gasto', 'danger')
        else:
            flash('No se pudo conectar a la base de datos', 'danger')
        return redirect(url_for('index'))

    print("Aplicación Flask creada exitosamente")
    return app

def obtener_info_app():
    return {
        'nombre': Config.APP_NAME,
        'version': Config.API_VERSION,
        'descripcion': 'API REST para control de gastos personales'
    }
