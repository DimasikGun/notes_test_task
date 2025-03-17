# Notes with AI and analytics

## About implementation decisions

The task was to create notes management system via FastAPI + SQLAlchemy with AI integration 
for notes summarization and statistics across notes using appropriate libraries.

* For users authentication I decided to use JWT, so this public repository contains RSA keys, which won`t be used 
anywhere else due to security considerations. I added it here just for ease of use and clarity.

* As DB, I am using Postgresql with SQLAlchemy(as in requirements) and Alembic for migrations.
I created script that filling db with **user (username="string", password="String123!")** and 3 notes with 
history (previous versions) on docker project start.

* As AI service, I am using Google Gemini AI, so before running project, you will need to generate 
[API KEY](https://aistudio.google.com/apikey) and paste into [.env.template](.env.template). 

* For testing, I was using Pytest with "pytest-asyncio" and "pytest-mock" plugins. And for linting and formatting 
I was using Ruff. 
To run tests, see coverage, and inspect if code is stick to PEP8
you will need to run project in Docker(guide below in **"Running project"** part) and run next commands:
```bash
docker exec -it notes_test_task-web-app-1 sh
```
that will start interactive shell, so you can work with project inside docker 
```bash
coverage run -m pytest 
```
to test, and
```bash
coverage report
```
to see coverage.

Then 
```bash
ruff check
```
to see if code stick to PEP8.

Use
Then 
```bash
exit 
```
to exit 
interactive shell
---



## API Endpoints:
all of it you can find at: [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/) when project started.

base url = /api/v1 
#### AUTH:
base url = /auth

* **(POST)** /sign_up - for registration
* **(POST)** /login - for singing in
* **(GET)** /me - for getting user info
* **(POST)** /refresh - to get a new pair of tokens by only refresh token

#### NOTES:
base url = /notes
* **(GET)** / - get all notes of authed user
* **(GET)** /{note_id} - get single note of authed user
* **(POST)** / - create a note for an authed user
* **(DELETE)** /{note_id} - delete a note of an authed user
* **(PATCH)** /{note_id} - update a note of an authed user
* **(GET)** /history/{note_id} - get single note of authed user with a previous versions of itself

#### ANALYTICS:
base url = /analytics
* **(GET)** / - get analytics across all notes (no authentication need)
* **(GET)** /notes - get all notes of all users (no authentication need)

### Technology stack:

* FastAPI + Pydantic
* Postgresql
* SQLAlchemy(asyncpg) + Alembic
* Google Gemini AI
* Pandas
* Docker
* JWT - for auth
* Ruff - as linter
* Pytest - as testing tool


---


## Running project

To run this project you will need Docker installed

### Step 1: Download Docker

First of all download Docker from official website: [Docker Official Website](https://www.docker.com/)

### Step 2: Running contaiters

In the root directory of project(notes_test_task) run next command:

```bash
docker compose up -d
```

To start project in docker.

**When all the containers got status "Started", and db container "Healty",
you can start working**

### Step 3: Stopping project

After all work done you will need to stop containers by the:

```bash
docker compose down
```
