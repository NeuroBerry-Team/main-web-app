# Proyecto Modular CUCEI

# Como levantar todo el sistema en entorno de desarrollo
Antes de nada, borrar toooodas las imagenes y containers de docker relacionados al modular.

## PRUNE a todo docker
Para borrar todo sin importar nada, correr: 
```sh
docker system prune -a
```

## PRUNE manual
Hazle como dicte chat gpt

## Levantar Web App
Pasos para iniciar la App

0. En tu carpeta preferida crea dos archivos, un archivo llamado `app-flask-errors.log` y otro llamado `nn-flask-errors.log`.
    > En estos archivos se guardaran los logs de error de la webApp y de la NN .

1. En la carpeta raíz del repo ubicar el archivo `.env_template` y hacer una copia del mismo con el nombre `.env.` (sobreescribirlo si lo pide). Una vez creado el archivo `.env` abrirlo y configurar *SOLO* las variables de entorno de desarrollo.
    > No olvides apuntar `FLASK_LOGFILE_PATH` al archivo `app-flask-errors.log` creado en el paso anterior

2. En la carpeta raíz ubicar el archivo `initPg_template.sh` y hacer una copia del mismo con el nombre `initPg.sh`.

3. En la carpeta raíz ubicar el archivo `populateDB_template.sh` y hacer una copia del mismo con el nombre `populateDB.sh`. Una vez creado el archivo `populateDB.sh` abrirlo y cambiar el password del usuario por una password encriptada con `Bcrypt` y un salt de `10` (Preguntar a chatgpt como hacer la encriptación)

4. En la carpeta `api-brain-mapper` ubicar el archivo `.env.format` y hacer una copia del mismo con el nombre `.env` (sobreescribirlo si lo pide). Una vez creado el archivo `.env` abrirlo y configura lo sig:
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

Rellena las DB configs faltantes con lo que se configuro en el punto 1. Deja las S3 configs faltantes para después. Y no olvides que en `NN_API_URL` cambia se '<host_ip>' por tu ip o 'localhost' y en `NN_API_SECRET_KEY` se cambia `<nn_api_secret_key>` por la secret key que planeas usar en la `ANN`.

5. En la carpeta `webclient-brain-mapper` ubicar el archivo `.env.format` y hacer una copia del mismo con el nombre `.env`. Una vez creado el archivo `.env` abrirlo y configurar:
```env
VITE_API_BASE_URL=http://<host_ip>:5000
```
Cambia `<host_ip>` por tu ip o `localhost`.


6. Una vez configurados todos los servicios, procede iniciar los contenedores de docker con el comando `docker compose -f docker-compose.dev.yml up`.

7. Cuando los contenedores ya estén prendidos, será hora de poblar la Base de Datos. Usando la terminal, ejecutar el comando `docker ps` y ubicar el hash del container `web-app-postgres-1`. Una vez ubicado copiarlo y ejecutar el siguiente comando: `docker exec -it {hash_copiado} /bin/sh`.

8. Después de haber ejecutado el `docker exec`, ejecutar dentro de la terminal que se abrió el siguiente comando: `psql -U {DB_USER} -d {DB_NAME} -f /home/populateDB.sql`.
    > Nota: Recuerda que `{DB_USER}` y `{DB_NAME}` son variables que configuraste en el paso 1, en este caso necesitas poner su valor explicito en lugar de `{DB_USER}`.

9. Después de que se haya ejecutado exitosamente el comando anterior, ejecutar `exit` para salir del contenedor de postgres.

10. En tu navegador favorito escribe http://localhost:9001, esto te llevará a la UI del S3. Ingresa las credenciales que pusiste para MINIO en el punto 1.

11. Una vez logeado haz click en 'Buckets' y da click en 'Create Bucket', crea un bucket llamado 'dataset' y otro llamado 'inferences'

12. Con los buckets creados, busca ambos buckets en la sección de 'Buckets' y da click al primero que veas, esto desplegará una interfaz. En esa interfaz busca la opción 'Anonymous'.

13. En la interfaz de 'Anonymous access' que acabas de acceder, da click en "Add Access Rule" y escribe "/" en el 'prefix' y selecciona 'readolny' en el accesso, por ultimo da click en 'Save'.

14. Repite los pasos 12 y 13 para el bucket faltante.

15. En la 'SideBar' de la izquierda, dar click en 'Access Keys' y dar click en 'Create access key' y un formulario será desplegado.

16. En el 'switch' llamado 'Restrict beyond user policy' cambialo a 'ON'.

17. El el bloque de texto desplegado por el paso anterior borra todo y pega lo sig:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
    "Effect": "Allow",
      "Action": [
          "s3:*"
      ],
      "Resource": [
          "arn:aws:s3:::dataset/*",
          "arn:aws:s3:::inferences/*"
      ]
    }
  ]
}
```

18. Rellena el formulario restante y elige una fecha de expiración adecuada para desarrollo 1 Año o lo que se te ocurra.

19. Da click en 'Create'. Una advertencia se mostrará y deberás asegurarte de guardar bien esa key.

20. Con las claves de acceso creadas, detén todos los contenedores (o solo el contenedor de flask_app), configura las claves de S3 en `api-brain-mapper/.env` y vuelve a iniciar el/los contenedor(es).


## Levantar ANN y su API
1. En la raiz del repo ubicar el archivo README.md y sigue sus instrucciones.