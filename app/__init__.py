from flask import Flask, jsonify
from flask_cors import CORS
from app.configuracion import Config
from app.base_datos import probar_conexion

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
    def pagina_inicio():
        """
        Ruta principal de la API
        Devuelve información básica sobre la aplicación
        """
        return jsonify({
            'aplicacion': Config.APP_NAME,
            'version': Config.API_VERSION,
            'mensaje': '¡Bienvenido a Gasto Track API!',
            'documentacion': {
                'endpoints_principales': {
                    'listar_gastos': 'GET /api/gastos',
                    'crear_gasto': 'POST /api/gastos',
                    'obtener_gasto': 'GET /api/gastos/{id}',
                    'actualizar_gasto': 'PUT /api/gastos/{id}',
                    'eliminar_gasto': 'DELETE /api/gastos/{id}',
                    'estadisticas': 'GET /api/gastos/estadisticas',
                    'categorias': 'GET /api/categorias'
                },
                'ejemplo_gasto': {
                    'descripcion': 'Almuerzo en restaurante',
                    'monto': 25.50,
                    'categoria': 'Alimentación',
                    'fecha': '2025-01-15'
                }
            },
            'estado': 'API funcionando correctamente'
        })
    
    @app.route('/health')
    def health_check():
        return jsonify({
            'estado': 'saludable',
            'timestamp': Config.obtener_timestamp_actual(),
            'version': Config.API_VERSION
        }), 200
    
    @app.errorhandler(404)
    def no_encontrado(error):
        return jsonify({
            'error': 'Endpoint no encontrado',
            'mensaje': 'La ruta solicitada no existe en esta API',
            'sugerencia': 'Revisa la documentación en GET /'
        }), 404
    
    @app.errorhandler(405)
    def metodo_no_permitido(error):
        return jsonify({
            'error': 'Método HTTP no permitido',
            'mensaje': 'El endpoint existe pero no acepta este método HTTP',
            'sugerencia': 'Verifica si debes usar GET, POST, PUT o DELETE'
        }), 405
    
    @app.errorhandler(500)
    def error_interno(error):
        return jsonify({
            'error': 'Error interno del servidor',
            'mensaje': 'Ocurrió un error inesperado',
            'sugerencia': 'Contacta al administrador si el problema persiste'
        }), 500
    
    @app.errorhandler(400)
    def solicitud_incorrecta(error):
        return jsonify({
            'error': 'Solicitud incorrecta',
            'mensaje': 'Los datos enviados no son válidos',
            'sugerencia': 'Revisa el formato JSON y los campos requeridos'
        }), 400
    
    
    @app.before_request
    def antes_de_cada_request():
        pass 
    
    @app.after_request
    def despues_de_cada_request(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    
    print("Aplicación Flask creada exitosamente")
    
    return app

def obtener_info_app():
    return {
        'nombre': Config.APP_NAME,
        'version': Config.API_VERSION,
        'descripcion': 'API REST para control de gastos personales'
    }