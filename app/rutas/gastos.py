from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from app.base_datos import obtener_coleccion_gastos
from app.modelos.gasto import Gasto, crear_gasto_desde_json
from app.configuracion import Config

gastos_bp = Blueprint('gastos', __name__)

# ========================================
# ENDPOINT 1: GET /api/gastos - LISTAR TODOS LOS GASTOS
# ========================================

@gastos_bp.route('/gastos', methods=['GET'])
def listar_gastos():

    try:
        coleccion = obtener_coleccion_gastos()
        if not coleccion:
            return jsonify({
                'error': 'No se pudo conectar a la base de datos'
            }), 500
        
        pagina = int(request.args.get('pagina', 1))
        limite = int(request.args.get('limite', Config.GASTOS_POR_PAGINA))
        categoria = request.args.get('categoria')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        filtros = {}
        
        if categoria:
            filtros['categoria'] = categoria
        
        if fecha_desde or fecha_hasta:
            filtros['fecha'] = {}
            if fecha_desde:
                filtros['fecha']['$gte'] = fecha_desde
            if fecha_hasta:
                filtros['fecha']['$lte'] = fecha_hasta
        
        saltar = (pagina - 1) * limite
        
        gastos_cursor = coleccion.find(filtros).sort('fecha', -1).skip(saltar).limit(limite)
        gastos = list(gastos_cursor)
        
        total_gastos = coleccion.count_documents(filtros)
        
        gastos_formateados = []
        for gasto in gastos:
            gasto_formateado = Gasto.formatear_para_respuesta(gasto)
            gastos_formateados.append(gasto_formateado)
        
        total_paginas = (total_gastos + limite - 1) // limite
        
        return jsonify({
            'gastos': gastos_formateados,
            'paginacion': {
                'pagina_actual': pagina,
                'total_paginas': total_paginas,
                'total_gastos': total_gastos,
                'gastos_por_pagina': limite,
                'tiene_siguiente': pagina < total_paginas,
                'tiene_anterior': pagina > 1
            },
            'filtros_aplicados': {
                'categoria': categoria,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta
            }
        })
        
    except ValueError as e:
        return jsonify({
            'error': 'Parámetros inválidos',
            'detalle': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }), 500

# ========================================
# ENDPOINT 2: GET /api/gastos/{id} - OBTENER UN GASTO ESPECÍFICO
# ========================================

@gastos_bp.route('/gastos/<string:gasto_id>', methods=['GET'])
def obtener_gasto(gasto_id):

    try:
        if not ObjectId.is_valid(gasto_id):
            return jsonify({
                'error': 'ID de gasto inválido',
                'detalle': 'El ID debe ser un ObjectId válido de MongoDB'
            }), 400
        
        coleccion = obtener_coleccion_gastos()
        if not coleccion:
            return jsonify({
                'error': 'No se pudo conectar a la base de datos'
            }), 500
        
        gasto = coleccion.find_one({'_id': ObjectId(gasto_id)})
        
        if not gasto:
            return jsonify({
                'error': 'Gasto no encontrado',
                'detalle': f'No existe un gasto con ID: {gasto_id}'
            }), 404
        
        gasto_formateado = Gasto.formatear_para_respuesta(gasto)
        return jsonify({
            'gasto': gasto_formateado
        })
        
    except InvalidId:
        return jsonify({
            'error': 'ID de gasto inválido'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }), 500

# ========================================
# ENDPOINT 3: POST /api/gastos - CREAR NUEVO GASTO
# ========================================

@gastos_bp.route('/gastos', methods=['POST'])
def crear_gasto():

    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({
                'error': 'No se enviaron datos',
                'detalle': 'El body del request debe contener JSON válido'
            }), 400
        
        gasto, errores = crear_gasto_desde_json(datos)
        
        if not gasto:
            return jsonify({
                'error': 'Datos inválidos',
                'errores': errores
            }), 400
        
        coleccion = obtener_coleccion_gastos()
        if not coleccion:
            return jsonify({
                'error': 'No se pudo conectar a la base de datos'
            }), 500
        
        resultado = coleccion.insert_one(gasto.to_dict())
        
        gasto_creado = coleccion.find_one({'_id': resultado.inserted_id})
        gasto_formateado = Gasto.formatear_para_respuesta(gasto_creado)
        
        return jsonify({
            'mensaje': 'Gasto creado exitosamente',
            'gasto': gasto_formateado
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }), 500

# ========================================
# ENDPOINT 4: PUT /api/gastos/{id} - ACTUALIZAR GASTO
# ========================================

@gastos_bp.route('/gastos/<string:gasto_id>', methods=['PUT'])
def actualizar_gasto(gasto_id):
    """
    Endpoint para actualizar un gasto existente
    """
    try:
        if not ObjectId.is_valid(gasto_id):
            return jsonify({
                'error': 'ID de gasto inválido'
            }), 400
        
        datos = request.get_json()
        if not datos:
            return jsonify({
                'error': 'No se enviaron datos para actualizar'
            }), 400
        
        es_valido, errores = Gasto.validar_datos(datos)
        if not es_valido:
            return jsonify({
                'error': 'Datos inválidos',
                'errores': errores
            }), 400
        
        coleccion = obtener_coleccion_gastos()
        if not coleccion:
            return jsonify({
                'error': 'No se pudo conectar a la base de datos'
            }), 500
        
        gasto_existente = coleccion.find_one({'_id': ObjectId(gasto_id)})
        if not gasto_existente:
            return jsonify({
                'error': 'Gasto no encontrado'
            }), 404
        
        datos_actualizacion = {
            'descripcion': datos['descripcion'].strip(),
            'monto': float(datos['monto']),
            'categoria': datos['categoria'],
            'fecha': datos.get('fecha', gasto_existente['fecha']),
            'fecha_actualizacion': datetime.now()
        }
        
        coleccion.update_one(
            {'_id': ObjectId(gasto_id)},
            {'$set': datos_actualizacion}
        )
        
        gasto_actualizado = coleccion.find_one({'_id': ObjectId(gasto_id)})
        gasto_formateado = Gasto.formatear_para_respuesta(gasto_actualizado)
        
        return jsonify({
            'mensaje': 'Gasto actualizado exitosamente',
            'gasto': gasto_formateado
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }), 500

# ========================================
# ENDPOINT 5: DELETE /api/gastos/{id} - ELIMINAR GASTO
# ========================================

@gastos_bp.route('/gastos/<string:gasto_id>', methods=['DELETE'])
def eliminar_gasto(gasto_id):
    try:

        if not ObjectId.is_valid(gasto_id):
            return jsonify({
                'error': 'ID de gasto inválido'
            }), 400
        
        coleccion = obtener_coleccion_gastos()
        if not coleccion:
            return jsonify({
                'error': 'No se pudo conectar a la base de datos'
            }), 500
        
        gasto = coleccion.find_one({'_id': ObjectId(gasto_id)})
        if not gasto:
            return jsonify({
                'error': 'Gasto no encontrado'
            }), 404
        
        resultado = coleccion.delete_one({'_id': ObjectId(gasto_id)})
        
        if resultado.deleted_count == 0:
            return jsonify({
                'error': 'No se pudo eliminar el gasto'
            }), 500
        
        return jsonify({
            'mensaje': 'Gasto eliminado exitosamente',
            'gasto_eliminado': Gasto.formatear_para_respuesta(gasto)
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }), 500

# ========================================
# ENDPOINT 6: GET /api/gastos/estadisticas - ESTADÍSTICAS
# ========================================

@gastos_bp.route('/gastos/estadisticas', methods=['GET'])
def obtener_estadisticas():

    try:
        coleccion = obtener_coleccion_gastos()
        if not coleccion:
            return jsonify({
                'error': 'No se pudo conectar a la base de datos'
            }), 500
        
        pipeline_categoria = [
            {
                '$group': {
                    '_id': '$categoria',
                    'total': {'$sum': '$monto'},
                    'cantidad': {'$sum': 1}
                }
            },
            {
                '$sort': {'total': -1} 
            }
        ]
        
        estadisticas_categoria = list(coleccion.aggregate(pipeline_categoria))
        
        total_general = sum(cat['total'] for cat in estadisticas_categoria)
        total_gastos = sum(cat['cantidad'] for cat in estadisticas_categoria)
        
        estadisticas_formateadas = []
        for stat in estadisticas_categoria:
            porcentaje = (stat['total'] / total_general * 100) if total_general > 0 else 0
            estadisticas_formateadas.append({
                'categoria': stat['_id'],
                'total': round(stat['total'], 2),
                'cantidad': stat['cantidad'],
                'porcentaje': round(porcentaje, 2)
            })
        
        return jsonify({
            'resumen': {
                'total_general': round(total_general, 2),
                'total_gastos': total_gastos,
                'promedio_por_gasto': round(total_general / total_gastos, 2) if total_gastos > 0 else 0
            },
            'por_categoria': estadisticas_formateadas
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }), 500

# ========================================
# ENDPOINT 7: GET /api/categorias - LISTAR CATEGORÍAS
# ========================================

@gastos_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    return jsonify({
        'categorias': Config.CATEGORIAS_PERMITIDAS
    })