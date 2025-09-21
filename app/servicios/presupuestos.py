# 📊 Sistema de Presupuestos - Implementación Rápida

from flask import request, jsonify, flash, redirect, url_for
from app.config.base_datos import obtener_db
from datetime import datetime
import calendar

class PresupuestoService:
    @staticmethod
    def crear_presupuesto(categoria, limite_mensual, usuario_id=None):
        db = obtener_db()
        presupuesto = {
            'categoria': categoria,
            'limite_mensual': float(limite_mensual),
            'mes': datetime.now().month,
            'año': datetime.now().year,
            'usuario_id': usuario_id,
            'fecha_creacion': datetime.now(),
            'activo': True
        }
        return db.presupuestos.insert_one(presupuesto)
    
    @staticmethod
    def obtener_presupuestos_activos():
        db = obtener_db()
        return list(db.presupuestos.find({'activo': True}))
    
    @staticmethod
    def calcular_progreso_presupuesto(categoria):
        db = obtener_db()
        mes_actual = datetime.now().month
        año_actual = datetime.now().year
        
        # Obtener presupuesto de la categoría
        presupuesto = db.presupuestos.find_one({
            'categoria': categoria,
            'mes': mes_actual,
            'año': año_actual,
            'activo': True
        })
        
        if not presupuesto:
            return None
            
        # Calcular gastos del mes actual
        gastos_mes = db.gastos.aggregate([
            {
                '$match': {
                    'categoria': categoria,
                    '$expr': {
                        '$and': [
                            {'$eq': [{'$month': {'$dateFromString': {'dateString': '$fecha', 'format': '%d-%m-%Y'}}}, mes_actual]},
                            {'$eq': [{'$year': {'$dateFromString': {'dateString': '$fecha', 'format': '%d-%m-%Y'}}}, año_actual]}
                        ]
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total_gastado': {'$sum': '$monto'}
                }
            }
        ])
        
        gastos_list = list(gastos_mes)
        total_gastado = gastos_list[0]['total_gastado'] if gastos_list else 0
        
        porcentaje_usado = (total_gastado / presupuesto['limite_mensual']) * 100
        
        return {
            'categoria': categoria,
            'limite': presupuesto['limite_mensual'],
            'gastado': total_gastado,
            'restante': presupuesto['limite_mensual'] - total_gastado,
            'porcentaje_usado': round(porcentaje_usado, 1),
            'estado': get_estado_presupuesto(porcentaje_usado)
        }
    
    @staticmethod
    def obtener_alertas_presupuesto():
        alertas = []
        categorias = ['Alimentación', 'Transporte', 'Entretenimiento', 'Salud', 'Educación', 'Otros']
        
        for categoria in categorias:
            progreso = PresupuestoService.calcular_progreso_presupuesto(categoria)
            if progreso and progreso['porcentaje_usado'] >= 80:
                alertas.append({
                    'categoria': categoria,
                    'porcentaje': progreso['porcentaje_usado'],
                    'tipo': 'warning' if progreso['porcentaje_usado'] < 100 else 'danger'
                })
        
        return alertas

def get_estado_presupuesto(porcentaje):
    if porcentaje >= 100:
        return 'excedido'
    elif porcentaje >= 80:
        return 'alerta'
    elif porcentaje >= 60:
        return 'moderado'
    else:
        return 'seguro'

# Integración en rutas principales
def agregar_rutas_presupuesto(app):
    @app.route('/presupuestos')
    def presupuestos():
        presupuestos_activos = PresupuestoService.obtener_presupuestos_activos()
        alertas = PresupuestoService.obtener_alertas_presupuesto()
        
        # Calcular progreso para cada presupuesto
        progresos = []
        for presupuesto in presupuestos_activos:
            progreso = PresupuestoService.calcular_progreso_presupuesto(presupuesto['categoria'])
            if progreso:
                progresos.append(progreso)
        
        return render_template('presupuestos.html', 
                             presupuestos=progresos, 
                             alertas=alertas)
    
    @app.route('/presupuestos/crear', methods=['POST'])
    def crear_presupuesto():
        categoria = request.form.get('categoria')
        limite = request.form.get('limite')
        
        if not categoria or not limite:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('presupuestos'))
        
        try:
            PresupuestoService.crear_presupuesto(categoria, float(limite))
            flash(f'Presupuesto para {categoria} creado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al crear presupuesto: {str(e)}', 'danger')
        
        return redirect(url_for('presupuestos'))