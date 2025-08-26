# Proyecto Modular CUCEI

# Como levantar todo el sistema en entorno de desarrollo
Antes de nada, borrar todas las imagenes y containers de docker relacionados al modular.

## PRUNE a todo docker
Para borrar todo sin importar nada, correr: 
```sh
docker system prune -a
```
**Nota**: Algunas veces es necesario remover los volumenes para evitar problemas con postgres, minio u otros servicios:
```sh
docker compose -f docker-compose.dev.yml down -v
```
o para borrar todo:
```sh
docker volume prune -f
```

## PRUNE manual
Hazle como dicte chat gpt

## Levantar Web App
Pasos para iniciar la App

0. En tu carpeta preferida crea dos archivos, un archivo llamado `app-flask-errors.log` y otro llamado `nn-flask-errors.log`.
    > En estos archivos se guardaran los logs de error de la webApp y de la NN .

1. En la carpeta raíz del repo ubicar el archivo `.env_template` y hacer una copia del mismo con el nombre `.env.` (sobreescribirlo si lo pide). Una vez creado el archivo `.env` abrirlo y configurar *SOLO* las variables de entorno de desarrollo.
    > No olvides apuntar `FLASK_LOGFILE_PATH` al archivo `app-flask-errors.log` creado en el paso anterior
    > **IMPORTANTE**: Ahora también debes configurar `S3_ACCESS_KEY` y `S3_SECRET_KEY` con las credenciales que quieras usar para tu aplicación (estos serán creados automáticamente)

2. En la carpeta raíz ubicar el archivo `initPg_template.sh` y hacer una copia del mismo con el nombre `initPg.sh`.

3. En la carpeta `api-brain-mapper` ubicar el archivo `.env.format` y hacer una copia del mismo con el nombre `.env` (sobreescribirlo si lo pide). Una vez creado el archivo `.env` abrirlo y configura lo sig:
```env
ENV_MODE=development

# DB conifgs
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_URL=postgres
SECRET_KEY=ultrasecret

# S3 configs
S3_BUCKET_DATASET=dataset
S3_BUCKET_INFERENCES_RESULTS=inferences
S3_HOST=s3
S3_PORT=9000
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_LIVE_BASE_URL=http://localhost:9000/
S3_PRESIGNED_EXPIRATION=600

NN_API_HOST=http://<host_ip>:8080/inferencia
NN_API_SECRET_KEY=<nn_api_secret_key>
``` 

### ¿Cómo generar una secret key con Python?

Puedes generar una secret key segura ejecutando el siguiente comando en tu terminal:

```sh
python -c "import secrets; print(secrets.token_hex(32))"
```

Esto imprimirá una cadena aleatoria de 64 caracteres hexadecimales, ideal para usar como `SECRET_KEY` o `NN_API_SECRET_KEY`.

5. En la carpeta `webclient-brain-mapper` ubicar el archivo `.env.format` y hacer una copia del mismo con el nombre `.env`. Una vez creado el archivo `.env` abrirlo y configurar:
```env
VITE_API_BASE_URL=http://<host_ip>:5000
```
Cambia `<host_ip>` por tu ip o `localhost`.


6. Una vez configurados todos los servicios, procede iniciar los contenedores de docker con el comando `docker compose -f docker-compose.dev.yml up`.
    > **NOTA**: El sistema ahora configurará automáticamente MinIO/S3 con los buckets necesarios, políticas y usuarios. No necesitas hacer configuración manual de S3.

7. El sistema se inicializará automáticamente con las migraciones de base de datos, creando todas las tablas necesarias y un usuario SUPERADMIN por defecto.
   - **Email**: admin@gmail.com  
   - **Password**: Pass$612345
   
   > **IMPORTANTE**: Cambia la contraseña del usuario SUPERADMIN después del primer login por seguridad.

¡Listo! la aplicación ya está configurada y funcionando. Puedes acceder a:
- **Web App**: http://localhost:3003
- **API Flask**: http://localhost:5000
- **MinIO Console**: http://localhost:9001 (usa las credenciales MINIO_ROOT_USER y MINIO_ROOT_PASSWORD o las del app user)
- **PostgreSQL**: localhost:5432

## Levantar ANN y su API
1. En la raiz del repo ubicar el archivo README.md y sigue sus instrucciones.


## Notas sobre la configuración automática de S3/MinIO

El sistema ahora incluye configuración automática de MinIO/S3 que elimina la necesidad de configuración manual. El script `setup-minio.sh` se ejecutara automáticamente cuando inicia el contenedor `mc` y realiza las siguientes tareas:

1. **Crea buckets automáticamente**: `dataset` e `inferences`
2. **Configura acceso público**: Establece permisos de lectura anónima para ambos buckets
3. **Crea usuario de aplicación**: Usa las credenciales especificadas en `S3_ACCESS_KEY` y `S3_SECRET_KEY`
4. **Aplica políticas**: Configura automáticamente las políticas de acceso desde `minio-policy.json`

### Archivos de configuración:
- `setup-minio.sh`: Script de configuración automática
- `minio-policy.json`: Definición de políticas de acceso

## Sobre el Script y Buckets
`setup-minio.sh` Configura automaticamente todo, si se va a hacer uso de entrenamiento en la API de la red neuronal, entonces se requiere tambien de una carpeta datasets.

### Troubleshooting:
Si necesitas verificar que la configuración se aplicó correctamente:
```bash
# Verificar buckets creados
docker compose exec mc mc ls local

# Verificar usuarios
docker compose exec mc mc admin user list local

# Verificar políticas
docker compose exec mc mc admin policy list local
```
