This document assumes that we have already created a Vagrant Cloud account, 
which we can access/create on the following link: https://app.vagrantup.com/account/new

Also, we will run this on an UNIX system. My personal recommendation is Ubuntu server.
It lacks a visible interface (console only) but it's pretty lightweight (less than 2gb the last Long Term Support version)
and, best of all, free


Steps:

1. Fork the project pressing the fork button on:

```
https://github.com/aliciapj/shield
```

This way we'll have created our own copy of the project on our repository

2. Download from your repository the contents using

```
git clone git_clone_address
```

Where "git_clone_address" is the text which you can get selecting ssh at the code button.
This will create a copy on the folder we have cd-ed to, so it is advisable it is empty

3. Create a virtual environment using
```
python3 -m venv .venv
```

4. Activate said virtual environment
```
source .venv/bin/activate
```

5. Install required libraries running
```
pip3 install -r requirements.txt
```

6. Execute migrations with
```
python3 manage.py migrate
```

7. Load the data from `superheroes.csv` using `metahumans/management/commands/load_from_csv.py`. 
   If you have problems running this command, run the following
```
python3 manage.py loaddata metahumans/fixtures/initial_data.json
```

8. Create your own django superuser:
```
python3 manage.py createsuperuser
```

9. Run the Django server to check on the app. It is advisable to run "check" first
```
python3 manage.py check
python3 manage.py runserver
```

## Vagrant

1. We open a Vagrant folder on our clone
```
vagrant init
```

2. We modify our file so we have the following rows uncommented
```
Vagrant.configure("2") do |config|
config.vm.box = "hashicorp/username"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "private_network", ip: "192.168.33.10"
  end
```
username being our vagrant user name

3. We check everything is alright running ``vagrant up`` and ``ssh vagrant_account``.
Being vagrant_account our vagrant account

## Fabric 

This steps are for setting up our project using fabric

1. First, we will install fabric on our system running this command
```
sudo apt install fabric
```

2. For our fabfile file, we'll use the original with some changes. It's found on
```
REPO_URL = "https://github.com/aliciapj/shield.git"
```
Appart from the tasks that the django polls fabfile already has, we add two more, a check and a runserver:
```
For a quicker reference, use the fabfile.py on this project

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

3. We run this with:
```
fab development deploy
```
CAUTION, this won't work unless we run ``vagrant up`` beforehand. 

4. This will have created a shield  folder and a virtual environment on our vagrant server. If we get into our Vagrant server, and we go to the project folder and from there to the venv one,
   and we run again ``fab development deploy`` we'll see how our project starts to be deployed

## Docker

1. We'll create a dockerfile (no extension) on our project root

2. Our dockerfile will be as the provided, except changing the WORKDIR with
```
WORKDIR /shield
```

3. Then we run: 
```
docker build -t shield .
``` 

This will create a docker image of our project.

4. With our image generated, we check it's there running:
```
docker images
```
Which will show an image of our project, shield

5. Then we run our project on local with:
```
docker run --publish 8000:8000 shield
curl localhost:8000
```

6. Or as a backtask with:
```
docker run -d -p 8000:8000 shield
curl localhost:8000
```