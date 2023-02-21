# AML Experiment application
This application has been set up to run online listening experiments for music research. It presents questions, and typically audio stimuli, to participants, and collects their feedback.

The application consists of a backend in Django (Python), and a frontend in React (JavaScript). Upon load, the frontend makes a call to the backend's `experiment` endpoint. The `experiment` application contains `actions` (i.e., data to be serialized for frontend views: all actions have a corresponding frontend component), `questions` (i.e., texts for demographic questions or questions on musical expertise) and `rules` (i.e., the description of an experiment's logic). A call to `experiment/slug` will locate the rules associated with the slug, and return the rule's `first_round`. The `first_round` usually consists of a number of actions: an explanation of the experiment, a consent form (registered with the `Participant`), optionally a view to select a playlist, and will then create the `Session` for that experiment. Note that the `first_round` cannot contain any actions which require passing a `result_id`, as these require a `Session` to work.

The frontend will then request data for the next views via `session/next_round`, which is provided via the rules' `next_round` function. This typically contains a `Trial` or another view requesting user feedback. A `Result` is created for each user feedback, and its `result_id` is included in the response. It may also include a `section` id, to be loaded from the `section` endpoint. Once the user gives feedback, this is sent to the `result/score` endpoint, which registers the user's response, optionally assigns a score, and then makes another call to the rules' `next_round` function.

`Result`s can either be *profile* type results, i.e., they are demographic information associated with a participant, and not expected to change. There is an option to avoid asking profile questions multiple times through the `experiment.questions.utils.unansked_question` function. `Result`s can also be tied to a *session* instead, and ideally give insights into the phenomena an experiment is set up to test.

After each result, the participant may get feedback in a `Score` view, and at the end of the experiment, they will be presented with a `Final` view, which may include their final score, as well as links for sharing in social media, and a personalized link which gives them an overview of the experiments they participated in.

## Install Docker
To run the application locally, you will need to install Docker.

### Mac OS X or Windows 10
Install [Docker Desktop](https://docs.docker.com/desktop/).

### Linux
* Install [Docker Engine](https://docs.docker.com/engine/install/)
* Install [Docker Compose](https://docs.docker.com/compose/install/)

As of April 2022, [Docker Desktop for Linux](https://docs.docker.com/desktop/linux/) is still in Beta and have not been tested by us.

## Development build
Make a file called .env next in this directory, with the following settings. Change database name and user and passwords as appropriate. The only setting that you'll have to set later is the slug, which depends on the slug (short name) of an existing experiment in your database.
```
SQL_DATABASE=aml
SQL_USER=aml
SQL_PASSWORD=supersecretpassword
SQL_HOST=db
SQL_PORT=5432

AML_SECRET_KEY=secretdjangopassword
AML_LOCATION_PROVIDER=http://ip2country:5000/{}
AML_DEBUG=True
DJANGO_SETTINGS_MODULE=aml.development_settings

REACT_APP_API_ROOT=http://localhost:8000
REACT_APP_EXPERIMENT_SLUG=your_slug
REACT_APP_AML_HOME=https://www.amsterdammusiclab.nl
```
Then, open a console and run
`docker-compose up` (add `sudo` on Linux).
This command makes use of the `docker-compose.yaml`, which defines four containers:
- a PostgreSQL container, for storing experiment/user/playlist data, saved on the host machine in the Docker user data, represented in the volume `db_data`. Data added to the database will persist if the container is shut down.
- a ip2country container, which provides country codes for ip addresses. This container is mainly interesting for running tests during development.
- a container of the server, defined in DockerfileDevelop in `backend`. The Dockerfile defines the Python version and installs development dependencies. The startup command runs migrations and then starts up a Django development server.
- a container of the client, defined in DockerfileDevelop in `frontend`. The Dockerfile defines the node version and installs node modules. The startup command kicks off a React development server.

Since the `docker-compose.yaml` defines bind mounts for `backend` and `frontend`, any changes to the files on the host are immediately reflected in the containers, which means code watching works and hot reload works in the same way as with a native node or Django server.

To stop the containers, press `ctrl-c` or (in another console) run
`docker-compose down`.

### Backup the Postgresql database
Run the following command in the console to back up the database:

`docker-compose run db bash -c "pg_dump aml -Fc > /backups/<filename>.dump"`

Use this command to make daily backups, numbered by the day of the month:

`docker-compose run db bash -c "pg_dump aml -Fc > /backups/backup-$(date +"%d").dump"`

The backups are stored on the docker volume `db_backup` which mirrors `/backups` from the Postgresql container.

### Restore the postgresq database

Always stop the backend container first:

`docker stop aml-experiments_server_1`

Then drop, create and restore the database:

`docker-compose run db bash -c "dropdb aml"`

`docker-compose run db bash -c "createdb aml"`

`docker-compose run db bash -c "pg_restore -d aml /backups/<filename>.dump"`

Restart the backend container: (or alternatively rebuilt the containers as descibed above) 

`docker start aml-experiments_server_1`

### Creating experiments and playlists
The admin interface is accessible at `localhost:8000/admin`. Before logging in, create a superuser by logging into the container of the backend. To find out the name, run `docker ps`, it should list all running container names. The container of the backend is most likely called `aml-experiments_server_1` (check 'NAMES' column). To connect to it, run:
`docker exec -it aml-experiments_server_1 bash`
This lets you execute shell commands on the container.
Then run `./manage.py createsuperuser`, and proceed to enter username, password and email address as prompted. After that, you can log into the admin interface to create a playlist and experiment. Make sure to adjust `REACT_APP_EXPERIMENT_SLUG` in your .env file accordingly.

### Compiling a playlist and other management commands
You can run management commands, such as dump the database or compile the playlist, by using the management container, as specified in `docker-compose-manage.yaml`.

For instance, to compile a playlist:
`docker-compose -f docker-compose-manage.yaml run manage ./manage.py compileplaylist path_to_sound_folder`

Other important management commands:
- Export experiment data to json: `./manage.py exportexperiment your_slug`
- Export how often sections have been played: `./manage.py exportplaycount playlist_id`
- Update translation strings in .po file: `./manage.py makemessages -l nl` or `./manage.py makemessages --all`
- Compile translations into binary .mo file: `./manage.py compilemessages`

### Debugging
If all containers are running via docker-compose, it is not possible to interact with the debug shell. Therefore, you need to do the following:
`docker ps` to list all running containers
`docker rm -f name_of_server_container`
`docker-compose run --rm --service-ports server`
After that, if you place a `breakpoint()` anywhere in the code, you can step through and inspect values of variables.

### Compile and watch scss files
The frontend container will build .css and .css.map files from scss every time you restart the Docker containers. To watch for and immediately see changes during development, run an extra client container like so:
`docker-compose run client yarn scss-watch`

## Production build
A production build should define its own `docker-compose.yaml`, making use of the `Dockerfile` of the `backend` and `frontend` environments. Instead of mounting the entire backend and frontend directory and using the development servers, the backend should serve with gunicorn, and the frontend should build its files. An example of this setup can be found in the aml-deployment repository.

Creating superusers or running management commands will work in essentially the same way as documented above for the development setting.
