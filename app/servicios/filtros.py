from datetime import datetime, timedelta
from flask import request, jsonify
from app.config.base_datos import obtener_db
import re

class FiltroService:
    @staticmethod
    def filtrar_gastos(filtros):
        """
        Filtros disponibles:
        - fecha_inicio: formato DD-MM-YYYY
        - fecha_fin: formato DD-MM-YYYY
        - categorias: lista de categorías
        - origen: tipo de origen
        - monto_min: monto mínimo
        - monto_max: monto máximo
        - busqueda: texto a buscar en descripción
        """
        db = obtener_db()
        query = {}
        
        if filtros.get('fecha_inicio') or filtros.get('fecha_fin'):
            fecha_query = {}
            if filtros.get('fecha_inicio'):
                fecha_query['$gte'] = filtros['fecha_inicio']
            if filtros.get('fecha_fin'):
                fecha_query['$lte'] = filtros['fecha_fin']
            query['fecha'] = fecha_query
        
        if filtros.get('categorias') and len(filtros['categorias']) > 0:
            query['categoria'] = {'$in': filtros['categorias']}
        
        if filtros.get('origen'):
            query['origen'] = filtros['origen']

        if filtros.get('monto_min') or filtros.get('monto_max'):
            monto_query = {}
            if filtros.get('monto_min'):
                monto_query['$gte'] = float(filtros['monto_min'])
            if filtros.get('monto_max'):
                monto_query['$lte'] = float(filtros['monto_max'])
            query['monto'] = monto_query
        
        if filtros.get('busqueda'):
            query['descripcion'] = {
                '$regex': re.escape(filtros['busqueda']),
                '$options': 'i'
            }
        
        gastos = list(db.gastos.find(query).sort('fecha', -1))
        
        for gasto in gastos:
            gasto['id'] = str(gasto['_id'])
            del gasto['_id']
        
        return gastos
    
    @staticmethod
    def obtener_estadisticas_filtradas(gastos_filtrados):
        """Calcula estadísticas para los gastos filtrados"""
        if not gastos_filtrados:
            return {
                'total': 0,
                'promedio': 0,
                'cantidad': 0,
                'por_categoria': [],
                'por_origen': []
            }
        
        total = sum(gasto['monto'] for gasto in gastos_filtrados)
        cantidad = len(gastos_filtrados)
        promedio = total / cantidad if cantidad > 0 else 0
        
        categorias = {}
        for gasto in gastos_filtrados:
            cat = gasto['categoria']
            categorias[cat] = categorias.get(cat, 0) + gasto['monto']
        
        por_categoria = [
            {'categoria': cat, 'total': total}
            for cat, total in sorted(categorias.items(), key=lambda x: x[1], reverse=True)
        ]
        
        origenes = {}
        for gasto in gastos_filtrados:
            orig = gasto['origen']
            origenes[orig] = origenes.get(orig, 0) + gasto['monto']
        
        por_origen = [
            {'origen': orig, 'total': total}
            for orig, total in sorted(origenes.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return {
            'total': round(total, 2),
            'promedio': round(promedio, 2),
            'cantidad': cantidad,
            'por_categoria': por_categoria,
            'por_origen': por_origen
        }
    
    @staticmethod
    def obtener_rangos_sugeridos():
        """Obtiene rangos de fechas comunes para filtros rápidos"""
        hoy = datetime.now()
        
        return {
            'hoy': {
                'inicio': hoy.strftime('%d-%m-%Y'),
                'fin': hoy.strftime('%d-%m-%Y'),
                'label': 'Hoy'
            },
            'esta_semana': {
                'inicio': (hoy - timedelta(days=hoy.weekday())).strftime('%d-%m-%Y'),
                'fin': hoy.strftime('%d-%m-%Y'),
                'label': 'Esta semana'
            },
            'este_mes': {
                'inicio': hoy.replace(day=1).strftime('%d-%m-%Y'),
                'fin': hoy.strftime('%d-%m-%Y'),
                'label': 'Este mes'
            },
            'ultimos_7_dias': {
                'inicio': (hoy - timedelta(days=7)).strftime('%d-%m-%Y'),
                'fin': hoy.strftime('%d-%m-%Y'),
                'label': 'Últimos 7 días'
            },
            'ultimos_30_dias': {
                'inicio': (hoy - timedelta(days=30)).strftime('%d-%m-%Y'),
                'fin': hoy.strftime('%d-%m-%Y'),
                'label': 'Últimos 30 días'
            }
        }

def agregar_endpoints_filtros(app):
    @app.route('/api/gastos/filtrar', methods=['POST'])
    def filtrar_gastos_api():
        filtros = request.get_json() or {}
        
        try:
            gastos_filtrados = FiltroService.filtrar_gastos(filtros)
            estadisticas = FiltroService.obtener_estadisticas_filtradas(gastos_filtrados)
            
            return jsonify({
                'success': True,
                'gastos': gastos_filtrados,
                'estadisticas': estadisticas,
                'total_resultados': len(gastos_filtrados)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
    
    @app.route('/api/filtros/rangos', methods=['GET'])
    def obtener_rangos_api():
        rangos = FiltroService.obtener_rangos_sugeridos()
        return jsonify(rangos)