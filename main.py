import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import crear_app
import os
from dotenv import load_dotenv
from app.config.configuracion import Config

load_dotenv()

app = crear_app()

if __name__ == '__main__':
    
    puerto = int(os.getenv('PORT', getattr(Config, 'PORT', 5000)))
    host = os.getenv('HOST', getattr(Config, 'HOST', '0.0.0.0'))
    debug_mode = os.getenv('DEBUG', 'True').lower() == 'true'

    print("Iniciando Gasto Track API")
    print(f"Servidor ejecutándose en: http://{host}:{puerto}")

    app.run(
        host=host,
        port=puerto,
        debug=debug_mode
    )