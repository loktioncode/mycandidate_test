# My Candidate flask template

## Technical Specs for QA
* Python 3.10.8 / 3.10.9
* postgresql 12.6.* or later
* Redis 7.x or later

## Website Environments
- [Production Environment](https://southafrica.mycandidate.africa/)

## Quick Start with Docker/Podman

The easiest way to run MyCandidate is using Docker Compose (or Podman Compose), which sets up the application, PostgreSQL database, and Redis cache automatically.

### Prerequisites
- Docker Desktop/Docker Engine 20.10+ OR Podman 4.0+
- Docker Compose 2.0+ OR podman-compose

### Running with Docker/Podman Compose

1. **Clone the repository**:
   ```bash
   git clone https://github.com/opendatadurban/mycandidate.git
   cd mycandidate
   ```

2. **Start all services**:
   ```bash
   # For Docker
   docker-compose up -d
   
   # For Podman
   podman-compose up -d
   ```

3. **Wait for services to be healthy** (about 30-60 seconds):
   ```bash
   # Check service status
   docker-compose ps
   # or
   podman-compose ps
   ```

4. **Initialize the database**:
   ```bash
   # For Docker
   docker-compose exec web python rebuild_db.py
   
   # For Podman
   podman-compose exec web python rebuild_db.py
   ```

5. **Access the application**:
   - Web interface: http://localhost:5001
   - API health check: http://localhost:5001/api/v1/health

### Docker/Podman Compose Services

- **web**: Flask application (mapped to port 5001 on host, 5000 in container)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)

### Useful Docker/Podman Commands

```bash
# View logs
docker-compose logs -f web
# or
podman-compose logs -f web

# Stop all services
docker-compose down
# or
podman-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
# or
podman-compose down -v

# Rebuild containers
docker-compose build --no-cache
# or
podman-compose build --no-cache

# Execute commands in web container
docker-compose exec web python rebuild_db.py
# or
podman-compose exec web python rebuild_db.py

# Access database
docker-compose exec db psql -U mycandidate -d mycandidate
# or
podman-compose exec db psql -U mycandidate -d mycandidate
```

### Building the Docker/Podman Image

To build the image manually:

```bash
# For Docker
docker build -t mycandidate:latest .

# For Podman
podman build -t mycandidate:latest .
```

### Environment Variables

Key environment variables (can be set in `.env` file or `docker-compose.yml`):

- `FLASK_ENV`: Environment (development/production)
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

## API Documentation

The MyCandidate application provides a REST API for accessing candidate data.

### Quick API Examples

**Health Check**:
```bash
curl http://localhost:5001/api/v1/health
```

**Get Candidates by Ward**:
```bash
curl http://localhost:5001/api/v1/wards/WARD001/candidates
```

**Get Candidates by Ward and Type**:
```bash
curl http://localhost:5001/api/v1/wards/WARD001/candidates?candidate_type=local
```

## Backend Setup (Traditional)
### Setting up a virtual environment with Python and pip
* clone the repo
* install a virtual env and activate it: `python -m venv env; env/Scripts/activate`[Windows]
* install a virtual env and activate it: `virtualenv --no-site-packages env; source env/bin/activate`[Linux/iOS]
* install requirements: `pip install -r requirements.txt`
* copy the configuration file: `cp dexter/config/example.development.cfg dexter/config/development.cfg`.

### Setting up a virtual anaconda environment with Python and pip
* clone the repo
* install a virtual conda env: `conda create -n mycandidate`
* activate the conda env: `source activate mycandidate`  
_for the VS Code IDE, make sure the new environment is set as the python interpreter_
* install requirements: `pip install -r requirements.txt`  
  _If errors are thrown, comment out the package in package.json, and handle afterwards individually. Uncomment package when committing back into repo_

### Setting up the Database with PostgreSQL
Setup the PostgreSQL database (minimum version 12.*)
```
psql -U postgres
=# CREATE USER mycandidate WITH PASSWORD 'mycandidate_<country_code>';
=# CREATE DATABASE mycandidate_<country_code>;
=# GRANT ALL PRIVILEGES ON DATABASE mycandidate_<country_code> TO mycandidate;
=# \q
```
- i.e mycandidate_<country_code> = mycandidate_za
Construct your db app-side:
```
from main.models import db
from main.models.seeds import seed_db
run 'python rebuild_db.py'
```

### Deploying database changes
* mycandidate App uses Flask-Migrate (which uses Alembic) to handle database migrations.
* To add a new model or make changes, update the SQLAlchemy definitions in `main/models/`. Then run
`alembic revision -m "create account table"`
* This will autogenerate a change. Double check that it make sense. To apply it on your machine, run
`alembic upgrade head`
* To downgrade all versions, this ultimately delete all tables
`alembic downgrade base`
  

### Pytest
- Powershell Run: `$ENV:PYTHONPATH = "<name-of-project>"`
- Linux/Mac to set the environment path `export PYTOHNPATH=<name-of-project>`

Then run `pytest` for simple test summary or `pytest -vv` for detailed test summary

### Redis Setup
Redis is required for caching and background task management.

Install Redis:

1. On Mac OS X: `brew install redis`
2. On Windows: Use the Redis [MSI installer](https://github.com/microsoftarchive/redis/releases)
3. On Ubuntu: `sudo apt-get update && sudo apt-get install redis-server`
4. Update your `development.cfg` to include Redis configuration: `REDIS_URL = "redis://<redis-host>"`

**Note**: If using Docker Compose, Redis is automatically configured and available at `redis://redis:6379/0`

## AWS Deployment

For production deployment on AWS, see [AWS_ARCHITECTURE.md](AWS_ARCHITECTURE.md) for:
- ECS Fargate container orchestration
- RDS PostgreSQL database setup
- ElastiCache Redis configuration
- VPC networking setup
- Security best practices
- Scaling strategies
- Data residency compliance (af-south-1 region)

## CI/CD Pipeline

The project includes a Jenkins CI/CD pipeline (`Jenkinsfile`) with:
- Automated testing
- Security scanning (dependency, SAST, container, secrets)
- Docker image building
- AWS ECR deployment
- ECS service updates

## DevOps Suggested Improvements

1. **Fix health check endpoint**: Update health check from `/health` to `/api/v1/health` in Dockerfile and docker-compose.yml to match the actual API endpoint.

2. **Enable CSRF protection in production**: Currently `WTF_CSRF_ENABLED = False` in `main/app.py` - this is a security risk and should be enabled with proper configuration.

3. **Add resource limits to docker-compose.yml**: Set CPU and memory limits for all services to prevent resource exhaustion and improve stability.

4. **Implement structured logging**: Replace basic logging with structured JSON logging for better CloudWatch integration and log analysis.

5. **Add Infrastructure as Code (IaC)**: Create Terraform or CloudFormation templates to automate AWS infrastructure provisioning and ensure environment parity.