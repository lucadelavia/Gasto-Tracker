from app import crear_app
import os
from dotenv import load_dotenv

load_dotenv()

app = crear_app()

if __name__ == '__main__':
    puerto = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print("Iniciando Gasto Track API")
    print(f"Servidor ejecutándose en: http://localhost:{puerto}")
    
    app.run(
        host='0.0.0.0',
        port=puerto,
        debug=debug_mode
    )