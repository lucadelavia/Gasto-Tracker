from flask import Flask, jsonify, render_template, redirect, url_for, request, flash
from flask_cors import CORS
from app.configuracion import Config
from app.base_datos import probar_conexion
from app.servicios.gastos import listar_gastos, crear_gasto, obtener_gasto, editar_gasto, borrar_gasto as borrar_gasto_servicio
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
        gastos = listar_gastos()
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
                exito = crear_gasto(gasto)
                if exito:
                    flash('Gasto agregado exitosamente', 'success')
                else:
                    flash('No se pudo agregar el gasto', 'danger')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('nuevo_gasto'))
        return render_template('nuevo.html', categorias=categorias)

    @app.route('/editar/<gasto_id>', methods=['GET', 'POST'])
    def editar_gasto_view(gasto_id):
        categorias = Config.CATEGORIAS_PERMITIDAS
        gasto = obtener_gasto(gasto_id)
        if request.method == 'POST':
            descripcion = request.form.get('descripcion')
            monto = request.form.get('monto')
            fecha = request.form.get('fecha')
            categoria = request.form.get('categoria')
            origen = request.form.get('origen')
            if not descripcion or not monto or not categoria or not origen:
                flash('Todos los campos son obligatorios', 'danger')
                return redirect(url_for('editar_gasto_view', gasto_id=gasto_id))
            if categoria not in categorias:
                flash('Categoría inválida', 'danger')
                return redirect(url_for('editar_gasto_view', gasto_id=gasto_id))
            try:
                datos_actualizados = {
                    'descripcion': descripcion,
                    'monto': float(monto),
                    'categoria': categoria,
                    'origen': origen,
                    'fecha': fecha if fecha else None,
                    'fecha_actualizacion': datetime.now()
                }
                exito = editar_gasto(gasto_id, datos_actualizados)
                if exito:
                    flash('Gasto editado exitosamente', 'success')
                else:
                    flash('No se pudo editar el gasto', 'danger')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('editar_gasto_view', gasto_id=gasto_id))
        return render_template('nuevo.html', categorias=categorias, gasto=gasto, editar=True)

    @app.route('/borrar/<gasto_id>', methods=['POST'])
    def borrar_gasto_view(gasto_id):
        exito = borrar_gasto_servicio(gasto_id)
        if exito:
            flash('Gasto eliminado exitosamente', 'success')
        else:
            flash('No se pudo eliminar el gasto', 'danger')
        return redirect(url_for('index'))

    print("Aplicación Flask creada exitosamente")
    return app

def obtener_info_app():
    return {
        'nombre': Config.APP_NAME,
        'version': Config.API_VERSION,
        'descripcion': 'API REST para control de gastos personales'
    }
