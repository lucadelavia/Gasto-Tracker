# 💰 Gasto Tracker

Una aplicación web moderna y elegante para el seguimiento de gastos personales, desarrollada con Flask y MongoDB.

![GitHub](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1+-green.svg)

## ✨ Características

- 📊 **Dashboard moderno** con gráficos interactivos de categorías
- 💳 **Gestión completa de gastos** (agregar, editar, eliminar)
- 🔍 **Filtros avanzados** por fecha y categoría
- 📱 **Diseño responsivo** optimizado para móviles y desktop
- ⚡ **Interfaz sin recargas** con edición modal
- 🎨 **UI moderna** con Bootstrap 5 y diseño gradiente
- 🔧 **Arquitectura modular** con servicios y rutas separadas

## 🚀 Instalación

### Prerrequisitos
- Python 3.8 o superior
- MongoDB (local o remoto)
- Git

### Pasos de instalación

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/lucadelavia/gasto-track-api.git
   cd gasto-track-api
   ```

2. **Crea un entorno virtual**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**
   ```bash
   # Crea un archivo .env en la raíz del proyecto
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB=gasto_tracker
   PORT=5000
   DEBUG=True
   ```

5. **Ejecuta la aplicación**
   ```bash
   python main.py
   ```

6. **Accede a la aplicación**
   
   Abre tu navegador en `http://localhost:5000`

## 📁 Estructura del Proyecto

```
gasto-track-api/
├── app/
│   ├── config/
│   │   └── configuracion.py      # Configuración de la app
│   ├── modelos/
│   │   └── gasto.py              # Modelo de datos de gastos
│   ├── rutas/
│   │   └── gastos.py             # Rutas y endpoints
│   ├── servicios/
│   │   ├── gastos.py             # Lógica de negocio
│   │   ├── filtros.py            # Servicios de filtrado
│   │   └── presupuestos.py       # Servicios de presupuesto
│   ├── static/
│   │   ├── custom.css            # Estilos personalizados
│   │   └── main.js               # JavaScript principal
│   ├── templates/
│   │   └── index.html            # Plantilla principal
│   └── __init__.py               # Factory de la aplicación
├── scripts/
├── main.py                       # Punto de entrada
├── requirements.txt              # Dependencias
├── README.md                     # Este archivo
└── .env                          # Variables de entorno (crear)
```

## 🛠️ Tecnologías

- **Backend**: Flask 3.1+, PyMongo
- **Frontend**: Bootstrap 5, Chart.js, Jinja2, JavaScript modular
- **Base de datos**: MongoDB
- **Estilos**: CSS customizado con gradientes modernos
- **Configuración**: python-dotenv

## 🏗️ Arquitectura Frontend

### Separación de responsabilidades
- **HTML**: Estructura semántica en `app/templates/index.html`
- **CSS**: Estilos modulares en `app/static/custom.css`
- **JavaScript**: Lógica funcional en `app/static/main.js`

### Características del JavaScript
- ✅ **Modular**: Funciones organizadas por responsabilidad
- ✅ **Documentado**: JSDoc en todas las funciones
- ✅ **Manejo de errores**: Validaciones y logs de console
- ✅ **Event-driven**: Listeners configurados automáticamente
- ✅ **Reutilizable**: Funciones exportadas al scope global

### Funciones principales
- `initializeChart()`: Configuración de Chart.js
- `aplicarFiltros()`: Filtrado de tabla en tiempo real
- `editarGasto()`: Modal de edición con prefill
- `setupFormEnhancements()`: Mejoras visuales de formularios

## 📋 Uso

### Agregar un gasto
1. Completa el formulario en la página principal
2. Selecciona una categoría y origen
3. Haz clic en "Agregar Gasto"

### Filtrar gastos
1. Usa los filtros de fecha y categoría en la parte superior
2. Los resultados se actualizan automáticamente
3. El total se recalcula según los filtros aplicados

### Editar un gasto
1. Haz clic en el botón "Editar" de cualquier gasto
2. Modifica los datos en el modal que aparece
3. Guarda los cambios

### Ver estadísticas
- El gráfico de dona muestra la distribución por categorías
- Los colores son asignados automáticamente
- Hover sobre las secciones para ver detalles

## 🌐 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Página principal con dashboard |
| POST | `/agregar` | Agregar nuevo gasto |
| POST | `/editar` | Editar gasto existente |
| DELETE | `/borrar/<id>` | Eliminar gasto |
| GET | `/api/gastos` | Obtener todos los gastos (JSON) |

## 🔧 Configuración

La aplicación utiliza variables de entorno definidas en el archivo `.env`:

```env
# Configuración de MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB=gasto_tracker

# Configuración del servidor
PORT=5000
DEBUG=True

# Otras configuraciones opcionales
SECRET_KEY=your-secret-key-here
```

## 🚧 Desarrollo

### Estructura de código
- **Modelos**: Definición de esquemas de datos en `app/modelos/`
- **Servicios**: Lógica de negocio en `app/servicios/`
- **Rutas**: Endpoints HTTP en `app/rutas/`
- **Templates**: Vistas HTML en `app/templates/`
- **Configuración**: Settings en `app/config/`

### Agregar nuevas características
1. Crea el modelo en `app/modelos/`
2. Implementa la lógica en `app/servicios/`
3. Define las rutas en `app/rutas/`
4. Actualiza las plantillas si es necesario

## 👨‍💻 Autor

**lucadelavia**
- GitHub: [@lucadelavia](https://github.com/lucadelavia)
