# cryptosign

## Setup

### Requirement

- Python 2.7
  - pip
  - virtualenv
- tmux
- redis

### Rest API

```bash
cd restapi
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Event

```bash
cd event
npm i
```

## Database

### Setup database

- Rest API: `restapi/app/settings.py` edit SQLALCHEMY_DATABASE_URI in class `DevelopmentConfig`
- Event: `event/configs/index.js` edit key db in config object

Advance setup config: these config files will be ignored to git, your change will not influent to git.

- Rest API: `cp app/settings-default.cfg to app/settings.cfg` then edit config by yourself.
- Event: `cp configs/config-local-default.js to configs/config-local.js` then edit config by yourself.

### Create database

Connect to your MySQL server

```bash
CREATE DATABASE cryptosign CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci IF NOT EXISTS cryptosign;
```

### Migrate database

```bash
cd restapi
python manage.py db migrate
python manage.py db upgrade
```

## Run

### Rest API

```bash
cd restapi
python wsgi.py
```

### Event

```bash
cd event
npm start
```

### Celery

```bash
cd restapi
celery -A app.tasks:celery worker --loglevel=info
```

## Test

### How to run

```bash
py.test tests/routes/*.py
```

## Deployment

### Installation

#### GCloud

Download and setup with doc: https://cloud.google.com/sdk/downloads

```bash
gcloud init
gcloud auth application-default login
```

#### SOLR

```
- /usr/local/Cellar/solr/7.3.1/server/solr/handshakes
```

#### Kubernetes

https://kubernetes.io/docs/tasks/tools/install-kubectl/
