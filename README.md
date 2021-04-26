# Note.it

Before running any commands, please make sure that you have both `tox` and
`docker` installed as they are mandatory for the development process.

Useful references:
- `https://docs.docker.com/engine/install`
- `https://tox.readthedocs.io/en/latest/install.html`

## Quickstart

Running below commands will result in setting up the development environment.

```shell
tox -e dev-db-up
tox -e dev-manage db upgrade
tox -e dev-run
``` 

For more details regarding the above commands, please look below.

## Workflow

### Updating the requirements

This projects uses `pip-tools` to handle the requirements.
To regenerate the requirements files, use the following command:

```shell
tox -e compile
```

### Performing quality checks

To run the linter:

```shell
tox -e lint
```

To automatically reformat all files:

```shell
tox -e black
```

To verify the code formatting:

```shell
tox -e black-check
```

To run all tests:

```shell
tox -e test
```

To run all tests with coverage:

```shell
tox -e test-cov
```

### Starting the database

Database is run under the `postgres` container using `docker-compose`
to avoid `postgres` dependencies on the Host OS. This however, creates
a requirement for the Host OS to have `docker` installed.

To start the database in background (detached mode):

```shell
tox -e dev-db-up
```

### Shutting down the database

To shut down the database `postgres` container:

```shell
tox -e dev-db-down
```

**WARNING: Since database data is not shared with Host OS,
this will result in removing all data from database!**

### Initializing the database

Application exposes the interface for interacting with database
and performing database migrations on a data schema changes.

To initialize the database:

```shell
tox -e dev-manage db init
```

To perform migration:

```shell
tox -e dev-manage db migrate
tox -e dev-manage db upgrade
```

### Running the application

To run the application in development mode:

```shell
tox -e dev-run
```

To access the application, simply go to the `http://127.0.0.1:5000`.

### Deploying the application

To deploy the application:

```shell
tox -e deploy
```

To access the application, simply go to the `http://127.0.0.1`.
