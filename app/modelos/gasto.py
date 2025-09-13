from datetime import datetime
from bson import ObjectId
from app.configuracion import Config

class Gasto:
    
    def __init__(self, descripcion, monto, categoria, fecha=None):
        self.descripcion = descripcion
        self.monto = monto
        self.categoria = categoria
        self.fecha = fecha if fecha else datetime.now().strftime('%d-%m-%Y')
        self.fecha_creacion = datetime.now()
        self.fecha_actualizacion = datetime.now()
    
    def to_dict(self):
        return {
            'descripcion': self.descripcion,
            'monto': self.monto,
            'categoria': self.categoria,
            'fecha': self.fecha,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion
        }
    
    @staticmethod
    def from_dict(data):
        gasto = Gasto(
            descripcion=data.get('descripcion'),
            monto=data.get('monto'),
            categoria=data.get('categoria'),
            fecha=data.get('fecha')
        )
        
        if 'fecha_creacion' in data:
            gasto.fecha_creacion = data['fecha_creacion']
        if 'fecha_actualizacion' in data:
            gasto.fecha_actualizacion = data['fecha_actualizacion']
            
        return gasto
    
    @staticmethod
    def validar_datos(data):
        errores = []
        
        if not data.get('descripcion'):
            errores.append('La descripción es obligatoria')
        elif len(data['descripcion'].strip()) < 3:
            errores.append('La descripción debe tener al menos 3 caracteres')
        elif len(data['descripcion']) > 100:
            errores.append('La descripción no puede tener más de 100 caracteres')

        monto = data.get('monto')
        if monto is None:
            errores.append('El monto es obligatorio')
        else:
            try:
                monto_float = float(monto)
                if monto_float <= 0:
                    errores.append('El monto debe ser mayor a 0')
                elif monto_float > 999999.99:
                    errores.append('El monto es demasiado grande')
            except (ValueError, TypeError):
                errores.append('El monto debe ser un número válido')
        
        categoria = data.get('categoria')
        if not categoria:
            errores.append('La categoría es obligatoria')
        elif categoria not in Config.CATEGORIAS_PERMITIDAS:
            errores.append(f'La categoría debe ser una de: {", ".join(Config.CATEGORIAS_PERMITIDAS)}')
        
        fecha = data.get('fecha')
        if fecha:
            try:
                datetime.strptime(fecha, '%d-%m-%Y')
            except ValueError:
                errores.append('La fecha debe tener formato DD-MM-YYY (ej: 25-12-2025)')
        
        return len(errores) == 0, errores
    
    @staticmethod
    def formatear_para_respuesta(documento_mongo):

        if not documento_mongo:
            return None
            
        if '_id' in documento_mongo:
            documento_mongo['id'] = str(documento_mongo['_id'])
            del documento_mongo['_id']
        
        if 'fecha_creacion' in documento_mongo:
            documento_mongo['fecha_creacion'] = documento_mongo['fecha_creacion'].isoformat()
        if 'fecha_actualizacion' in documento_mongo:
            documento_mongo['fecha_actualizacion'] = documento_mongo['fecha_actualizacion'].isoformat()
        
        return documento_mongo
    
    def actualizar_fecha_modificacion(self):
        """
        Actualiza la fecha de modificación al momento actual
        """
        self.fecha_actualizacion = datetime.now()

def crear_gasto_desde_json(data):

    es_valido, errores = Gasto.validar_datos(data)
    if not es_valido:
        return None, errores
    
    gasto = Gasto(
        descripcion=data['descripcion'].strip(),
        monto=float(data['monto']),
        categoria=data['categoria'],
        fecha=data.get('fecha')
    )
    
    return gasto, []