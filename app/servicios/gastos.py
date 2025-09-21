from app.config.base_datos import obtener_coleccion_gastos
from app.modelos.gasto import Gasto
from app.config.configuracion import Config
from bson import ObjectId
from datetime import datetime
import pandas as pd

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


def estadisticas_por_categoria():
    coleccion = obtener_coleccion_gastos()
    if coleccion is None:
        return []
    gastos = list(coleccion.find())
    if not gastos:
        return []
    df = pd.DataFrame(gastos)
    if 'categoria' not in df or 'monto' not in df:
        return []
    resumen = df.groupby('categoria')['monto'].sum().reset_index()
    total = resumen['monto'].sum()

    colores = {
        "Alimentación": "#FF6384",
        "Transporte": "#36A2EB",
        "Entretenimiento": "#FFCE56",
        "Salud": "#4BC0C0",
        "Educación": "#9966FF",
        "Servicios": "#FF9F40",
        "Ropa": "#C9CBCF",
        "Hogar": "#8DD17E",
        "Otros": "#E17C05"
    }
    resultado = []
    for categoria in Config.CATEGORIAS_PERMITIDAS:
        monto = float(resumen[resumen['categoria'] == categoria]['monto'].sum()) if categoria in resumen['categoria'].values else 0.0
        porcentaje = round((monto / total) * 100, 2) if total > 0 else 0
        resultado.append({
            'categoria': categoria,
            'total': monto,
            'porcentaje': porcentaje,
            'color': colores.get(categoria, '#CCCCCC')
        })
    return resultado
