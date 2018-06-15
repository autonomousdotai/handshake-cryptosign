# cryptosign

## Setup

### Requirement

- Python 2.7
  - pip
  - virtualenv
- tmux
- redis
- ipfs

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

### Testrpc

```bash
npm install -g ethereumjs-testrpc
```

### Ethereum

```bash
brew update
brew upgrade
brew tap ethereum/ethereum
brew install ethereum
```

### IPFS

```bash
ipfs init
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

```bash
tmux new-session -n handshake
cd /Workspace/robotbase/cryptosign/restapi && source/bin/activate && python wsgi.py
cd /Workspace/robotbase/cryptosign/event && npm start
testrpc -m 'merge void air robot execute perfect ghost drum sphere skin crawl fiction'
redis-server
cd /Workspace/robotbase/cryptosign/restapi && source/bin/activate && celery -A app.tasks:celery worker --loglevel=info
ipfs daemon
```

## Test

### How to run

```bash
py.test tests/routes/*.py
```

## Issues

### deploy staging

- [x] Blockchain server
- [x] Event
- [x] Rest API

### deploy production

- [ ] Blockchain server
- [ ] Event
- [ ] Rest API

### Conflict offchain value in Production

- [ ] Function encode/decode offchain value with prefix cryptosign_
- [ ] integrate to logic code event + restapi

### Server

- [ ] Mysql server - database for Event + Rest API
- [ ] Redis server - save blockchain transaction

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

```bash
gcloud auth application-default print-access-token
gcloud container clusters get-credentials server-cluster1 --zone us-west1-a --project handshake-205007
kubectl proxy + http://localhost:8001/ui
kubectl --namespace=staging get pods
kubectl --namespace=staging exec -it cryptosign-service-5d6759b94c-hr78j /bin/bash
```

#### Steps

REQUIRED:

- [] Mirgrate database
- [] Create tag version on github
- [] deploy.sh {tag_version} # deploy-util/deploy_neuron/staging-neuron/handshake-restapi/deploy.sh
