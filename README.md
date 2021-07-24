# Bienvenida a la applicación de SHIELD para Admin-Sistemas

Pasos a seguir:
1. Haz un fork del proyecto pulsando el botón fork en la pagina:

```
https://github.com/aliciapj/shield
```
Para que aparezca en nuestro repositorio de github una copia del proyecto.

2. Descarga el proyecto del repo con git usando el comando:

```
git clone git@github.com:AlpargataRauda/shield.git
```
Mientras estamos en una carpeta (si esta vacia mejor), que será desde donde trabajaremos.

3. Crea un entorno virtual mediante:
```
python3 -m venv .venv
```

4. Activa el entorno virtual:
```
source .venv/bin/activate
```

5. Instala las librerías del `requirements.txt` con:
```
pip install -r requirements.txt
```

6. Ejecuta las migraciones con:
```
python3 manage.py migrate
```

7. Carga los datos de superheroes del fichero `superheroes.csv` usando el comando `metahumans/management/commands/load_from_csv.py`. Si os da problemas usando el comando load_from_csv, podéis usar el comando ``loaddata`` con el fichero `metahumans/fixtures/initial_data.json`. En nuestro caso usaremos:
```
python3 manage.py loaddata metahumans/fixtures/initial_data.json
```

8. Crea tu propio usuario superuser para poder entrar en el admin de django:
```
python3 manage.py createsuperuser
```

9. Ejecuta el servidor de django para probar la aplicación, es recomendable hacer un check para ver que todo está correcto:
```
python3 manage.py check
python3 manage.py runserver
```

## Vagrant

1. Abrimos una carpeta de vagrant en la carpeta de nuestro miniproyecto.
```
vagrant init
```

2. Aquí modificamos el vagrant file de forma que solo queden descomentadas las siguientes lineas:
```
Vagrant.configure("2") do |config|
config.vm.box = "hashicorp/bionic64"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "private_network", ip: "192.168.33.10"
  end
```

3. Comprobamos que todo va bien con ``vagrant up`` y haciendo un ``ssh "nuestra cuenta de vagrant"``.

Esto será necesario para Fabric y Ansible.

## Fabric 

Pasos a seguir para abrir nuestro proyecto usando fabric:

1. Primero descargaremos fabric en nuestro entorno virtual con:
```
sudo apt install fabric
```

2. Para crear el fabfile necesario para abrir nuestro proyecto, copiaremos gran parte del fabfile de django polls visto en clase, con ciertas excepciones que comentaremos a continuación:
```
REPO_URL = "https://github.com/aliciapj/shield.git"
```
Ademas de las task que ya tiene el fabfile de django polls añadimos 2 más, un check y un runserver:
```
@task
def check(ctx):
    print("checking for issues...")

    if isinstance(ctx, Connection):
        conn = ctx
    else:
        conn = get_connection(ctx)

    with conn.cd(PROJECT_PATH):
        conn.run(f"{VENV_PYTHON} manage.py check")

@task
def deploy(ctx):
    conn = get_connection(ctx)
    if conn is None:
        sys.exit("Failed to get connection")

    clone(conn)
    checkout(conn, branch="main")
    pull(conn, branch="main")
    create_venv(conn)
    requeriments_install(conn)
    migrate(conn)
    loaddata(conn)
    check(conn)

@task
def runserver(ctx ,PROJECT_PATH="~/shield", port=8000):
    print("checking for issues...")

    if isinstance(ctx, Connection):
        conn = ctx
    else:
        conn = get_connection(ctx)

    with conn.cd(PROJECT_PATH):
        conn.run(f"{VENV_PYTHON} manage.py runserver 127.0.0.1:8000")
        conn.run(f"{VENV_PYTHON} curl 127.0.0.1:8000")

@task
def deploy(ctx):
    conn = get_connection(ctx)
    if conn is None:
        sys.exit("Failed to get connection")

    clone(conn)
    checkout(conn, branch="main")
    pull(conn, branch="main")
    create_venv(conn)
    requeriments_install(conn)
    migrate(conn)
    loaddata(conn)
    check(conn)
    runserver(conn)
```

3. Ejecutamos esto con:
```
fab development deploy
```
Ojo: Esto no lo hará a no ser que hayamos hecho un ``vagrant up`` antes. 

4. Luego, esto nos habrá creado una carpeta shield y un entorno virtual en nuestro servidor de vagrant. Si entramos en nuestro servidor, y dentro de aquí a la carpeta y al entorno virtual y ejecutamos el ``fab development deploy`` otra vez veremos como se despliega nuestro proyecto de shield.

## Ansible 

## Docker

1. En un principio crearemos un dockerfile en la raiz de la carpeta de nuestro proyecto.

2. Nuestro dockerfile será igual que el dockerfile que hicimos en clase, con la diferencia que el WORKDIR será diferente.
```
WORKDIR /shield
```

3. Con el comando: 
```
docker build -t shield .
``` 

Crearemos una imagen de docker del proyecto de shield.

4. Ahora que tenemos nuestra imagen generada podemos comprobar que está ahí con:
```
docker images
```
Aquí veremos una imagen de shield, nuestro proyecto.

5. Arrancaremos nuestro proyecto en nuestra red local con:
```
docker run --publish 8000:8000 shield
curl localhost:8000
```

6. También podemos arrancarlo en segundo plano con:
```
docker run -d -p 8000:8000 shield
curl localhost:8000
```