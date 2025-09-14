# NeuroBerry - Plataforma de Análisis Inteligente para Frambuesas

## 📋 Descripción del Proyecto

NeuroBerry es una plataforma modular desarrollada para la detección y clasificación automática del estado de madurez de frambuesas mediante técnicas de Visión por Computadora e Inteligencia Artificial. El sistema está diseñado para optimizar procesos de cosecha, mejorar el control de calidad y proporcionar trazabilidad en la producción agrícola.

### 🎯 Objetivos

- Automatizar la identificación del estado de madurez de frambuesas
- Reducir costos de mano de obra y variabilidad humana en la clasificación
- Proporcionar herramientas de análisis y visualización de datos
- Facilitar la toma de decisiones basada en datos para productores

### 🏗️ Arquitectura del Sistema

El sistema está compuesto por los siguientes componentes:

- **Frontend Web**: Aplicación Vue.js 3 con Tailwind CSS
- **API Principal**: Backend Flask con autenticación y gestión de datos
- **API de Inferencia**: Servicio FastAPI para procesamiento de imágenes con IA
- **Base de Datos**: PostgreSQL para persistencia de datos
- **Almacenamiento**: MinIO/S3 para gestión de imágenes y resultados
- **Infraestructura**: Docker Compose para orquestación de servicios

## 🚀 Guía de Instalación y Configuración

### 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.8+ (para generación de claves secretas)
- Git para clonar el repositorio
- Mínimo 4GB de RAM disponible
- Puertos disponibles: 3000, 5000, 5432, 9000, 9001

### 🔧 Configuración del Entorno de Desarrollo

#### 1. Preparación Inicial

**1.1 Limpieza del Sistema Docker (Opcional)**

Para evitar conflictos con instalaciones previas:

```bash
# Eliminar todos los recursos de Docker
docker system prune -a

# Eliminar volúmenes específicos del proyecto
docker compose -f docker-compose.dev.yml down -v

# Eliminar todos los volúmenes (usar con precaución)
docker volume prune -f
```

**1.2 Creación de Archivos de Logs**

Crear los siguientes archivos en una ubicación accesible:

```bash
touch /ruta/deseada/app-flask-errors.log
touch /ruta/deseada/nn-flask-errors.log
```

#### 2. Configuración de Variables de Entorno

**2.1 Configuración Principal del Proyecto**

1. Copiar el archivo de plantilla:

   ```bash
   cp .env_template .env
   ```

2. Editar `.env` y configurar las variables de desarrollo:

   ```env
   # Rutas de logs
   FLASK_LOGFILE_PATH=/ruta/absoluta/app-flask-errors.log
   
   # Credenciales S3/MinIO (serán creadas automáticamente)
   S3_ACCESS_KEY=tu_clave_acceso_personalizada
   S3_SECRET_KEY=tu_clave_secreta_personalizada
   ```

**2.2 Configuración del Script de Inicialización**

```bash
cp initPg_template.sh initPg.sh
```

**2.3 Configuración de la API Principal**

1. Navegar al directorio de la API:

   ```bash
   cd api-brain-mapper
   ```

2. Crear archivo de configuración:

   ```bash
   cp .env.format .env
   ```

3. Configurar las variables:

   ```env
   ENV_MODE=development

   # Configuración de Base de Datos
   DB_NAME=neurobberry_db
   DB_USER=neuroberry_user
   DB_PASSWORD=password_seguro_123
   DB_URL=postgres
   SECRET_KEY=clave_secreta_generada

   # Configuración de Almacenamiento S3
   S3_BUCKET_DATASET=dataset
   S3_BUCKET_INFERENCES_RESULTS=inferences
   S3_HOST=s3
   S3_PORT=9000
   S3_ACCESS_KEY=misma_clave_del_env_principal
   S3_SECRET_KEY=misma_clave_secreta_del_env_principal
   S3_LIVE_BASE_URL=http://localhost:9000/
   S3_PRESIGNED_EXPIRATION=600

   # Configuración de API de Inferencia
   NN_API_HOST=http://localhost:8080/inferencia
   NN_API_SECRET_KEY=clave_secreta_neural_api
   ```

**2.4 Configuración del Cliente Web**

1. Navegar al directorio del cliente:

   ```bash
   cd webclient
   ```

2. Crear archivo de configuración:

   ```bash
   cp .env.format .env
   ```

3. Configurar la URL de la API:

   ```env
   VITE_API_BASE_URL=http://localhost:5000
   ```

#### 3. Generación de Claves Secretas

Para generar claves seguras, utilice el siguiente comando:

```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('NN_API_SECRET_KEY=' + secrets.token_hex(32))"
```

### 🐳 Ejecución del Sistema

#### Inicio de Servicios

```bash
# Iniciar todos los servicios en modo desarrollo
docker compose -f docker-compose.dev.yml up -d

# O para ver todo en terminal
docker compose -f docker-compose.dev.yml up

# Ver logs en tiempo real
docker compose -f docker-compose.dev.yml logs -f
```

#### Verificación de Servicios

Una vez iniciado el sistema, los servicios estarán disponibles en:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Aplicación Web** | <http://localhost:3003> | Interfaz principal del usuario |
| **API Principal** | <http://localhost:5000> | API RESTful para gestión de datos |
| **Consola MinIO** | <http://localhost:9001> | Gestión de almacenamiento de archivos |
| **Base de Datos** | localhost:5432 | PostgreSQL (acceso directo) |

### 👤 Credenciales por Defecto

El sistema crea automáticamente un usuario administrador:

- **Email**: `admin@gmail.com`
- **Contraseña**: `Pass$612345`
- **Rol**: `SUPERADMIN`

> ⚠️ **Importante**: Cambiar la contraseña por defecto después del primer inicio de sesión.

## 🧠 Configuración de la API de Inferencia

Para configurar la API de Inferencia Neural, consulte la documentación específica en el archivo README correspondiente del módulo de IA.

## 🔧 Configuración Automática de MinIO/S3

El sistema incluye configuración automática de almacenamiento que elimina la configuración manual:

### Características Automatizadas

1. **Creación de Buckets**: `dataset` e `inferences`
2. **Configuración de Permisos**: Acceso público de lectura
3. **Gestión de Usuarios**: Creación automática con credenciales especificadas
4. **Aplicación de Políticas**: Configuración desde `minio-policy.json`

### Archivos de Configuración

- `setup-minio.sh`: Script de configuración automática
- `minio-policy.json`: Definición de políticas de acceso

### Verificación de Configuración

```bash
# Verificar buckets creados
docker compose exec mc mc ls local

# Verificar usuarios configurados
docker compose exec mc mc admin user list local

# Verificar políticas aplicadas
docker compose exec mc mc admin policy list local
```

## 🛠️ Solución de Problemas

### Problemas Comunes

1. **Error de puertos ocupados**: Verificar que los puertos 3000, 5000, 5432, 9000, 9001 estén disponibles
2. **Problemas de permisos**: Asegurar que Docker tenga permisos adecuados
3. **Falla de inicialización de BD**: Eliminar volúmenes y reiniciar contenedores
4. **Errores de MinIO**: Verificar credenciales S3 en archivos `.env`

### Comandos Útiles

```bash
# Reiniciar servicios específicos
docker compose -f docker-compose.dev.yml restart [servicio]

# Ver logs de un servicio específico
docker compose -f docker-compose.dev.yml logs -f [servicio]

# Eliminar y recrear servicios
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up -d --build

# Acceder a un contenedor
docker compose -f docker-compose.dev.yml exec [servicio] /bin/bash

# Acceder a la base de datos
docker exec -it web-app-main-postgres-1 psql -U myuser -d mydatabase
```

## 📚 Documentación Adicional

- **Guía de Usuario**: Consultar la sección "Proyecto" en la aplicación web (TBD)
- **API Reference**: Disponible en `http://localhost:5000/docs` (cuando esté implementado)
- **Base de Datos**: Esquema disponible en `migrations/versions/`

## 📄 Licencia

Este proyecto está desarrollado como parte de un proyecto académico en CUCEI - Universidad de Guadalajara.

---

**Desarrollado por**: Equipo Neuro Berry  
**Institución**: Centro Universitario de Ciencias Exactas e Ingenierías (CUCEI)  
**Fecha**: 2025
