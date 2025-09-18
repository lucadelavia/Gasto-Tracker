from app.base_datos import obtener_coleccion_gastos
from app.modelos.gasto import Gasto
from bson import ObjectId
from datetime import datetime

# Lógica de negocio para gastos

def listar_gastos():
    coleccion = obtener_coleccion_gastos()
    gastos = []
    if coleccion is not None:
        cursor = coleccion.find().sort('fecha', -1)
        for gasto in cursor:
            gastos.append(Gasto.formatear_para_respuesta(gasto))
    return gastos


def crear_gasto(data):
    coleccion = obtener_coleccion_gastos()
    if coleccion is not None:
        coleccion.insert_one(data)
        return True
    return False


def obtener_gasto(gasto_id):
    coleccion = obtener_coleccion_gastos()
    if coleccion is not None:
        gasto_db = coleccion.find_one({'_id': ObjectId(gasto_id)})
        if gasto_db:
            return Gasto.formatear_para_respuesta(gasto_db)
    return None


def editar_gasto(gasto_id, datos_actualizados):
    coleccion = obtener_coleccion_gastos()
    if coleccion is not None:
        resultado = coleccion.update_one({'_id': ObjectId(gasto_id)}, {'$set': datos_actualizados})
        return resultado.modified_count > 0
    return False


def borrar_gasto(gasto_id):
    coleccion = obtener_coleccion_gastos()
    if coleccion is not None:
        resultado = coleccion.delete_one({'_id': ObjectId(gasto_id)})
        return resultado.deleted_count > 0
    return False
