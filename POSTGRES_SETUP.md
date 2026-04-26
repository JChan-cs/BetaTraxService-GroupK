# PostgreSQL Setup for BetaTrax Sprint 3

This guide explains how to set up PostgreSQL for BetaTrax, which uses a single database with separate-schema multi-tenancy approach via `django-tenants`.

## Prerequisites

- PostgreSQL 13+ installed
- psycopg2-binary installed in your Python virtual environment
- django-tenants installed

## Option 1: Using Docker (Recommended)

### Start PostgreSQL with Docker Compose

```bash
# Navigate to project root
cd /Users/mct61674/Desktop/BetaTraxService-GroupK

# Start PostgreSQL container
docker-compose up -d

# Verify container is running
docker ps | grep betatrax_postgres
```

### Check Connection

```bash
# From your machine
psql -h localhost -U betatrax -d betatrax

# Expected output: connected to "betatrax" database
# Exit with: \q
```

### Stop PostgreSQL

```bash
docker-compose down
```

### Remove Data and Reset

```bash
docker-compose down -v
docker-compose up -d
```

## Option 2: Manual PostgreSQL Installation

### macOS

```bash
# Install PostgreSQL using Homebrew
brew install postgresql

# Start PostgreSQL service
brew services start postgresql

# Verify installation
psql --version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify
psql --version
```

### Windows

Download installer from [postgresql.org](https://www.postgresql.org/download/windows/) and follow the installation wizard.

## Create BetaTrax Database

```bash
# Connect to PostgreSQL as default user
psql -U postgres

# Create database
CREATE DATABASE betatrax;

# Create user for BetaTrax
CREATE USER betatrax WITH PASSWORD 'betatrax';

# Grant privileges
ALTER ROLE betatrax SET client_encoding TO 'utf8';
ALTER ROLE betatrax SET default_transaction_isolation TO 'read committed';
ALTER ROLE betatrax SET default_transaction_deferrable TO on;
ALTER ROLE betatrax SET default_transaction_deferrable TO off;
ALTER ROLE betatrax CREATEDB;

# Grant database permissions
GRANT ALL PRIVILEGES ON DATABASE betatrax TO betatrax;

# Exit PostgreSQL
\q
```

## Verify Connection from BetaTrax

```bash
# Navigate to project
cd /Users/mct61674/Desktop/BetaTraxService-GroupK/BetaTrax

# Test connection using Django
python manage.py dbshell
# Should show "betatrax=>" prompt
# Exit with: \q
```

## Initialize Tenant Schemas

```bash
cd /Users/mct61674/Desktop/BetaTraxService-GroupK/BetaTrax

# Run migrations on shared apps
python manage.py migrate

# Run migrations on all tenant schemas
python manage.py migrate_schemas --executor=sequential
```

## Troubleshooting

### Error: "FATAL: role 'betatrax' does not exist"

The user was not created. Run the creation commands above.

### Error: "could not connect to server"

PostgreSQL is not running. Start it:
- macOS: `brew services start postgresql`
- Linux: `sudo systemctl start postgresql`
- Docker: `docker-compose up -d`

### Error: "database 'betatrax' does not exist"

Create the database:
```bash
createdb -U postgres betatrax
```

### Connection refused on port 5432

PostgreSQL is not listening on localhost:5432. Verify:
- PostgreSQL is running
- Port 5432 is not blocked by firewall
- Settings are correct in demo/settings.py

## Database Settings in BetaTrax

The database settings are configured in `/Users/mct61674/Desktop/BetaTraxService-GroupK/BetaTrax/demo/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'betatrax',
        'USER': 'betatrax',
        'PASSWORD': 'betatrax',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

To modify connection details, edit this file and restart your Django application.

## Running Tests with PostgreSQL

Once PostgreSQL is set up and running, run tests:

```bash
cd /Users/mct61674/Desktop/BetaTraxService-GroupK/BetaTrax

# Run all tenant-aware tests
python manage.py test defects.tests

# Run with coverage
coverage run --source='.' manage.py test defects.tests
coverage report
```

## Cleanup

### Stop PostgreSQL (Docker)

```bash
docker-compose down
```

### Remove All Data (Docker)

```bash
docker-compose down -v
```

### macOS Local PostgreSQL

```bash
brew services stop postgresql
```
