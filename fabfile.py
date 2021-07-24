import sys
import os

from fabric import Connection, task

PROJECT_NAME = "shield"
PROJECT_PATH = f"~/{PROJECT_NAME}"
REPO_URL = "https://github.com/aliciapj/shield.git"
VENV_PYTHON = f'{PROJECT_PATH}/.venv/bin/python'
VENV_PIP = f'{PROJECT_PATH}/.venv/bin/pip'

@task
def development(ctx):
    ctx.user = 'vagrant'
    ctx.host = '192.168.33.10'
    ctx.connect_kwargs = {"password": "vagrant"}

@task
def deploy(ctx):
    with Connection(ctx.host, ctx.user, connect_kwargs=ctx.connect_kwargs) as conn:
        conn.run("uname")
        conn.run("ls")

def get_connection(ctx):
    try:
        with Connection(ctx.host, ctx.user, connect_kwargs=ctx.connect_kwargs) as conn:
            return conn
    except Exception as e:
        return None

@task
def deploy(ctx):
    conn = get_connection(ctx)
    if conn is None:
        sys.exit("Failed to get connection")

@task
def clone(ctx): 
    print(f"clone repo {REPO_URL}...")   
    if isinstance(ctx, Connection):
        conn = ctx
    else:
        conn = get_connection(ctx)
    # obtengo las carpetas del directorio
    ls_result = conn.run("ls").stdout
    # divido el resultado para tener cada carpeta en un objeto de una lista
    ls_result = ls_result.split("\n")
    # si el nombre del proyecto ya está en la lista de carpetas
    # no es necesario hacer el clone
    if PROJECT_NAME not in ls_result:
        conn.run(f"git clone {REPO_URL} {PROJECT_NAME}")
    else:
        print('Project already exists')


@task
def deploy(ctx):
    conn = get_connection(ctx)
    if conn is None:
        sys.exit("Failed to get connection")
    clone(conn)

@task
def checkout(ctx, branch=None):
    print(f"checkout to branch {branch}...")
    if branch is None:
        sys.exit("branch name is not specified")
    if isinstance(ctx, Connection):
        conn = ctx
    else:
        conn = get_connection(ctx)
    with conn.cd(PROJECT_PATH):
        conn.run(f"git checkout {branch}")

@task
def deploy(ctx):
    conn = get_connection(ctx)
    if conn is None:
        sys.exit("Failed to get connection")
    clone(conn)
    checkout(conn, branch="main")

@task
def pull(ctx, branch="main"):
    print(f"pulling latest code from {branch} branch...")

    if branch is None:
        sys.exit("branch name is not specified")

    if isinstance(ctx, Connection):
        conn = ctx
    else:
        conn = get_connection(ctx)
        
    with conn.cd(PROJECT_PATH):
        conn.run(f"git pull origin {branch}")

@task
def deploy(ctx):
    conn = get_connection(ctx)
    if conn is None:
        sys.exit("Failed to get connection")
    clone(conn)
    checkout(conn, branch="main")
    pull(conn, branch="main")

@task
def create_venv(ctx):

    print("creating venv....")

    if isinstance(ctx, Connection):
        conn = ctx
    else:
        conn = get_connection(ctx)
    with conn.cd(PROJECT_PATH):
        conn.run("python3 -m venv .venv")


@task
def deploy(ctx):
    conn = get_connection(ctx)
    if conn is None:
        sys.exit("Failed to get connection")

    clone(conn)
    checkout(conn, branch="main")
    pull(conn, branch="main")
    create_venv(conn)

@task
def requeriments_install(ctx):
    print("Installing requeriments...")

    if isinstance(ctx, Connection):
        conn = ctx
    else:
        conn = get_connection(ctx)

    with conn.cd(PROJECT_PATH):
        conn.run(f"{VENV_PIP} install -r requirements.txt")

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


@task
def migrate(ctx):
    print("checking for django db migrations...")

    if isinstance(ctx, Connection):
        conn = ctx
    else:
        conn = get_connection(ctx)

    with conn.cd(PROJECT_PATH):
        conn.run(f"{VENV_PYTHON} manage.py migrate")

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

@task
def loaddata(ctx):
    print("Loading resources...")

    if isinstance(ctx, Connection):
        conn = ctx
    else:
        conn = get_connection(ctx)

    with conn.cd(PROJECT_PATH):
        conn.run(f"{VENV_PYTHON} manage.py loaddata metahumans/fixtures/initial_data.json")
        # conn.sudo: Buscar en apuntes para instalar cosas en la maquina de vagrant
        #El README es una memoria de lo que estamos haciendo, decir lo que estamos copiando o cambiando
        #Se despliega en la maquina de vagrant, tanto fabric como ansible
        #En docker se hara de forma diferente, 
        #Se puede desplegar desde la maquina local si se pone localhost como host
        #Si no funciona ninguno de los comandos de sudo por errores temporales reiniciar la maquina virtual vagrant
         #sudo apt update
         #sudo apt install python3-pip
         #sudo apt install python3-venv
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