from flask import Blueprint, request, jsonify
from app.servicios.gastos import listar_gastos as listar_gastos_servicio, crear_gasto as crear_gasto_servicio, obtener_gasto as obtener_gasto_servicio, editar_gasto as editar_gasto_servicio, borrar_gasto as borrar_gasto_servicio
from app.modelos.gasto import Gasto, crear_gasto_desde_json
from app.configuracion import Config
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime


gastos_bp = Blueprint('gastos', __name__)

# ========================================
# ENDPOINT 1: GET /api/gastos - LISTAR TODOS LOS GASTOS
# ========================================

@gastos_bp.route('/gastos', methods=['GET'])
def listar_gastos():
    try:
        pagina = int(request.args.get('pagina', 1))
        limite = int(request.args.get('limite', Config.GASTOS_POR_PAGINA))
        categoria = request.args.get('categoria')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        # Filtros y paginación pueden implementarse en servicios si se desea
        gastos = listar_gastos_servicio()  # Por simplicidad, sin paginación avanzada
        return jsonify({'gastos': gastos})
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor', 'detalle': str(e)}), 500

# ========================================
# ENDPOINT 2: GET /api/gastos/{id} - OBTENER UN GASTO ESPECÍFICO
# ========================================

@gastos_bp.route('/gastos/<string:gasto_id>', methods=['GET'])
def obtener_gasto(gasto_id):
    try:
        gasto = obtener_gasto_servicio(gasto_id)
        if not gasto:
            return jsonify({'error': 'Gasto no encontrado'}), 404
        return jsonify({'gasto': gasto})
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor', 'detalle': str(e)}), 500

# ========================================
# ENDPOINT 3: POST /api/gastos - CREAR NUEVO GASTO
# ========================================

@gastos_bp.route('/gastos', methods=['POST'])
def crear_gasto():
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({'error': 'No se enviaron datos'}), 400
        gasto, errores = crear_gasto_desde_json(datos)
        if not gasto:
            return jsonify({'error': 'Datos inválidos', 'errores': errores}), 400
        exito = crear_gasto_servicio(gasto.to_dict())
        if not exito:
            return jsonify({'error': 'No se pudo agregar el gasto'}), 500
        return jsonify({'mensaje': 'Gasto creado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor', 'detalle': str(e)}), 500

# ========================================
# ENDPOINT 4: PUT /api/gastos/{id} - ACTUALIZAR GASTO
# ========================================

@gastos_bp.route('/gastos/<string:gasto_id>', methods=['PUT'])
def actualizar_gasto(gasto_id):
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({'error': 'No se enviaron datos para actualizar'}), 400
        exito = editar_gasto_servicio(gasto_id, datos)
        if not exito:
            return jsonify({'error': 'No se pudo editar el gasto'}), 500
        return jsonify({'mensaje': 'Gasto actualizado exitosamente'})
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor', 'detalle': str(e)}), 500

# ========================================
# ENDPOINT 5: DELETE /api/gastos/{id} - ELIMINAR GASTO
# ========================================

@gastos_bp.route('/gastos/<string:gasto_id>', methods=['DELETE'])
def eliminar_gasto(gasto_id):
    try:
        exito = borrar_gasto_servicio(gasto_id)
        if not exito:
            return jsonify({'error': 'No se pudo eliminar el gasto'}), 500
        return jsonify({'mensaje': 'Gasto eliminado exitosamente'})
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor', 'detalle': str(e)}), 500

# ========================================
# ENDPOINT 6: GET /api/categorias - LISTAR CATEGORÍAS
# ========================================

@gastos_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    return jsonify({'categorias': Config.CATEGORIAS_PERMITIDAS})