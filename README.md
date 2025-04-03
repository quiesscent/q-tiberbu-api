# Healthcare Appointment Scheduling System

This is a healthcare appointment scheduling system built using Django. It includes functionalities like patient and doctor management, appointment scheduling, and insurance details. The system uses PostgreSQL as the database and OAuth 2.0 for authentication.

## Prerequisites

Before you begin, ensure you have the following installed on your local machine:
* Python 3.8+
* pip (Python package installer)
* PostgreSQL
* Virtualenv (optional, but recommended)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/quiesscent/q-tiberbu-api.git
cd q-tiberbu-api
cd healthcare
```

### 2. Set up a Virtual Environment (Optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```


### 3. Install the required dependencies

Make sure your virtual environment is activated, then run:

```bash
pip install -r requirements.txt
```

### 4. Set up the Database

#### 4.1 Install PostgreSQL (if not already installed)
* Install PostgreSQL

#### 4.2 Create a PostgreSQL Database

1. Log into PostgreSQL:

```bash
psql -U postgres
```

2. Create a new database and user (replace `<your_db_name>`, `<your_username>`, and `<your_password>` with your own):

```sql
CREATE DATABASE healthcare_db;
CREATE USER <your_username> WITH PASSWORD '<your_password>';
ALTER ROLE <your_username> SET client_encoding TO 'utf8';
ALTER ROLE <your_username> SET default_transaction_isolation TO 'read committed';
ALTER ROLE <your_username> SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE healthcare_db TO <your_username>;
```

3. Exit PostgreSQL:

```bash
\q
```

#### 4.3 Update Django Settings

Open `settings.py` and modify the `DATABASES` setting to use PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'healthcare_db',  # Your database name
        'USER': '<your_username>',  # Your PostgreSQL username
        'PASSWORD': '<your_password>',  # Your PostgreSQL password
        'HOST': 'localhost',  # Or the host where your DB is running
        'PORT': '5432',
    }
}
```

### 5. Run Migrations

Run Django migrations to set up the database schema:

```bash
python manage.py migrate
```

### 6. Create a Superuser

To access the Django admin panel, create a superuser:

```bash
python manage.py createsuperuser
```

You'll be prompted to provide a username, email, and password, etc. for the superuser.

### 7. Run the Server

Now you can run the Django development server:

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

## Additional Configuration

### 1. OAuth2.0 Authentication
* The system uses OAuth2.0 for secure authentication. Ensure you have set up the `Django OAuth Toolkit` as per the instructions in the project.

### 2. Swagger/OpenAPI Documentation

The API documentation is available via Swagger UI at:

```
http://127.0.0.1:8000/swagger/
```

Ensure that you have set up `drf-yasg` for automatic generation of Swagger docs.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
