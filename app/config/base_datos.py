from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from dotenv import load_dotenv

load_dotenv()

class BaseDatos:
    _instancia = None
    _cliente = None
    _db = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(BaseDatos, cls).__new__(cls)
        return cls._instancia
    
    def conectar(self):
        try:
            mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/gastotrack')
            
            self._cliente = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000 
            )
            
            self._cliente.admin.command('ping')
            
            nombre_db = mongo_uri.split('/')[-1]
            self._db = self._cliente[nombre_db]
            
            print("Conexion exitosa a MongoDB")
            return True
            
        except ConnectionFailure as e:
            print(f"Error de conexion a MongoDB: {e}")
            return False
    
    def obtener_db(self):
        if self._db is None:
            self.conectar()
        return self._db
    
    def obtener_coleccion(self, nombre_coleccion):
        db = self.obtener_db()
        if db is not None:
            return db[nombre_coleccion]
        return None
    
    def cerrar_conexion(self):
        if self._cliente:
            self._cliente.close()
            self._cliente = None
            self._db = None
            print("Conexion a MongoDB cerrada")

def obtener_coleccion_gastos():

    bd = BaseDatos()
    return bd.obtener_coleccion('gastos')

def probar_conexion():
    try:
        bd = BaseDatos()
        if bd.conectar():
            print("MongoDB esta funcionando correctamente")
            gastos = obtener_coleccion_gastos()
            if gastos is not None:
                print(f"Colección 'gastos' accesible")
            return True
        else:
            print("No se pudo conectar a MongoDB")
            return False
    except Exception as e:
        print(f"Error probando conexion: {e}")
        return False