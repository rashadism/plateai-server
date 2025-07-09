# PlateAI Server

This is the backend server for PlateAI, built with FastAPI.

## Requirements
- Python 3.10+

## Installation
```bash
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
DB_SCHEMA=public
```

Adjust the values as needed for your PostgreSQL setup.

## Running the Server
```bash
uvicorn main:app --reload
```

The server will be available at http://127.0.0.1:8000

## Health Check
Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to verify the server is running.

## Running with Docker

### Prerequisites
- Docker installed on your system
- PostgreSQL database running (either locally or remotely)

### Environment Setup
1. Copy the environment example file:
```bash
cp env.example .env
```

2. Edit the `.env` file with your database credentials:
```
DATABASE_HOST=your_db_host
DATABASE_PORT=5432
DATABASE_USER=your_postgres_user
DATABASE_PASSWORD=your_postgres_password
DATABASE_NAME=plateai
SECRET_KEY=your_super_secret_key_for_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Building and Running the Docker Container

1. Build the Docker image:
```bash
docker build -t plateai-server .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env plateai-server
```

### Alternative: Using Docker Compose (Recommended)

If you want to run the server with a PostgreSQL database, create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: plateai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  server:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_HOST: db
      DATABASE_PORT: 5432
      DATABASE_USER: postgres
      DATABASE_PASSWORD: password
      DATABASE_NAME: plateai
      SECRET_KEY: your_super_secret_key_for_jwt
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
    depends_on:
      - db

volumes:
  postgres_data:
```

Then run:
```bash
docker-compose up --build
```

The server will be available at http://127.0.0.1:8000 