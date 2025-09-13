import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'revenge332025')
    
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/gastotrack')
    
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000')
    
    APP_NAME = "Gasto Track API"
    
    API_VERSION = "1.0.0"
    
    GASTOS_POR_PAGINA = 10

    CATEGORIAS_PERMITIDAS = [
        "Alimentación",
        "Transporte", 
        "Entretenimiento",
        "Salud",
        "Educación",
        "Servicios",
        "Ropa",
        "Hogar",
        "Otros"
    ]
    
    # === MÉTODOS ÚTILES ===
    @staticmethod
    def init_app(app):
        """
        Método para inicializar configuraciones adicionales si es necesario
        """
        pass