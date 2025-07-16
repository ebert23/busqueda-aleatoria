# Sistema de Gestión de Servicios Automotrices

Este sistema permite gestionar registros de servicios automotrices, incluyendo la importación masiva desde archivos Excel y búsqueda paginada de registros.

## Características

- Registro de servicios automotrices con detalles completos
- Importación masiva desde archivos Excel
- Búsqueda por número de placa
- Visualización paginada (500 registros por página)
- Cálculo automático de totales
- Interfaz responsive y amigable

## Requisitos

- Python 3.11 o superior
- Pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

2. Crear un entorno virtual:
```bash
python -m venv venv
```

3. Activar el entorno virtual:

En Windows:
```bash
venv\Scripts\activate
```

En Linux/Mac:
```bash
source venv/bin/activate
```

4. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Desarrollo Local

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones locales
```

3. Iniciar la aplicación:
```bash
python app.py
```

4. Abrir el navegador en `http://localhost:5000`

5. Iniciar sesión con:
   - Usuario: `admin`
   - Contraseña: `admin123`

## Despliegue en Render

### Opción 1: Usando render.yaml (Recomendado)
1. Hacer fork o clonar este repositorio
2. Conectar tu repositorio a Render
3. Render detectará automáticamente el archivo `render.yaml`
4. La aplicación se desplegará con la configuración predefinida

### Opción 2: Configuración Manual
1. Crear un nuevo Web Service en Render
2. Conectar tu repositorio
3. Configurar las siguientes variables de entorno:
   - `DATABASE_URL`: postgresql://cambiosdb_user:xJtg2cPzhBoMjQwABhv6j67TdQGqC21Q@dpg-d1pv1uvfte5s73cpnvf0-a.oregon-postgres.render.com/cambiosdb
   - `SECRET_KEY`: (generar una clave secreta segura)
   - `FLASK_ENV`: production
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python init_db.py && gunicorn app:app`

### Después del Despliegue
- La base de datos se inicializará automáticamente
- Se creará un usuario admin por defecto:
  - Usuario: `admin`
  - Contraseña: `admin123`
- **IMPORTANTE**: Cambiar la contraseña del admin después del primer login

## Formato del Archivo Excel para Importación

El archivo Excel debe contener las siguientes columnas:

- **FECHA**: Fecha del servicio (obligatorio)
- **PLACA**: Número de placa del vehículo (obligatorio)
- **CLIENTE**: Nombre del cliente
- **MARCA**: Marca del vehículo
- **MODELO**: Modelo del vehículo
- **KM**: Kilometraje

Columnas de servicios y precios:
- FILTRO DE ACEITE y PRECIO FILTRO ACEITE
- FILTRO DE AIRE y PRECIO FILTRO AIRE
- FILTRO DE PETROLEO y PRECIO FILTRO PETROLEO
- ACEITE DE MOTOR y PRECIO ACEITE DE MOTOR
- OTROS 1-4 y sus respectivos PRECIO OTROS 1-4

Notas:
- Los nombres de las columnas deben coincidir exactamente
- Los precios deben ser valores numéricos
- La primera fila debe contener los nombres de las columnas