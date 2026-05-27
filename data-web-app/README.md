# Data Web Application

A modern web application for data manipulation with support for CSV files and PostgreSQL database. Designed for Docker and Kubernetes deployment.

## Features

- **CSV Support**: Upload, query, and manage CSV datasets
- **PostgreSQL Support**: Full PostgreSQL database integration
- **REST API**: Comprehensive API with FastAPI
- **Docker Ready**: Complete Docker configuration
- **Kubernetes Ready**: Full Kubernetes manifests included
- **Data Querying**: Advanced querying with filters, sorting, and pagination
- **Statistics**: Get detailed statistics for your datasets

## Project Structure

```
data-web-app/
├── app/                          # Application code
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                # Configuration management
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── base.py              # Base models
│   │   └── dataset.py           # Dataset models
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   └── dataset.py           # Response schemas
│   ├── repositories/            # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py              # Repository interfaces
│   │   ├── csv_repository.py    # CSV implementation
│   │   └── postgres_repository.py  # PostgreSQL implementation
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   └── dataset_service.py   # Dataset operations
│   └── api/                     # API routes
│       ├── __init__.py
│       ├── datasets.py          # Dataset API endpoints
│       └── health.py            # Health check endpoints
├── data/                         # Data files
│   ├── csv/                     # CSV datasets
│   └── uploads/                 # Uploaded files
├── k8s/                         # Kubernetes manifests
│   ├── deployment.yaml          # Deployment configurations
│   ├── service.yaml            # Service configurations
│   ├── ingress.yaml            # Ingress configuration
│   ├── pvc.yaml                # Persistent volume claims
│   └── secrets.yaml            # Secrets configuration
├── nginx/                       # Nginx configuration
│   └── nginx.conf              # Nginx reverse proxy config
├── scripts/                    # Utility scripts
│   └── init.sql                # Database initialization
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose for local development
├── requirements.txt            # Python dependencies
├── .env.example                # Environment configuration template
└── README.md                   # This file
```

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use any text editor
```

### 3. Run with CSV (Default)

```bash
# For development
uvicorn app.main:app --reload

# For production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`

### 4. Run with Docker Compose (Full Stack)

```bash
# Start all services (web app + PostgreSQL + pgAdmin)
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

The application will be available at:
- Web App: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- pgAdmin: `http://localhost:5050`

### 5. Run with Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods

# Get service URL
kubectl get svc data-web-app-service

# View logs
kubectl logs -f deployment/data-web-app
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

### Main Endpoints

- **GET /** - Root endpoint
- **GET /api/v1/health** - Health check
- **GET /api/v1/ready** - Readiness check
- **GET /api/v1/datasets/** - List all datasets
- **POST /api/v1/datasets/** - Create a new dataset
- **GET /api/v1/datasets/{name}** - Get dataset details
- **DELETE /api/v1/datasets/{name}** - Delete a dataset
- **POST /api/v1/datasets/{name}/upload** - Upload CSV file
- **POST /api/v1/datasets/{name}/query** - Query dataset data
- **GET /api/v1/datasets/{name}/columns** - Get dataset columns
- **GET /api/v1/datasets/{name}/stats** - Get dataset statistics

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Data Web Application | Application name |
| `APP_VERSION` | 1.0.0 | Application version |
| `APP_DEBUG` | False | Debug mode |
| `APP_HOST` | 0.0.0.0 | Host to bind to |
| `APP_PORT` | 8000 | Port to bind to |
| `DATA_SOURCE` | csv | Data source (csv or postgres) |
| `CSV_DIRECTORY` | ./data/csv | CSV directory |
| `UPLOAD_DIRECTORY` | ./data/uploads | Upload directory |
| `DB_HOST` | localhost | Database host |
| `DB_PORT` | 5432 | Database port |
| `DB_NAME` | data_app | Database name |
| `DB_USER` | postgres | Database user |
| `DB_PASSWORD` | postgres | Database password |

### Switching Data Sources

To switch from CSV to PostgreSQL:

1. Set `DATA_SOURCE=postgres` in your `.env` file
2. Ensure PostgreSQL is running and accessible
3. Restart the application

## Data Operations

### CSV Operations

```bash
# Upload a CSV file
curl -X POST -F "file=@data.csv" "http://localhost:8000/api/v1/datasets/my_dataset/upload"

# List datasets
curl "http://localhost:8000/api/v1/datasets/"

# Query dataset
curl -X POST -H "Content-Type: application/json" \
  -d '{"limit": 10, "offset": 0}' \
  "http://localhost:8000/api/v1/datasets/my_dataset/query"
```

### PostgreSQL Operations

When using PostgreSQL, datasets are represented as database tables. The application automatically manages the connection and provides the same API interface.

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster
- kubectl configured
- Docker registry for your image

### Deployment Steps

1. **Build and push Docker image:**
   ```bash
   docker build -t your-registry/data-web-app:latest .
   docker push your-registry/data-web-app:latest
   ```

2. **Update Kubernetes manifests:**
   - Update image in `k8s/deployment.yaml`
   - Update secrets in `k8s/secrets.yaml`
   - Update ingress host in `k8s/ingress.yaml`

3. **Apply manifests:**
   ```bash
   kubectl apply -f k8s/
   ```

4. **Verify deployment:**
   ```bash
   kubectl get pods
   kubectl get svc
   kubectl get ingress
   ```

### Scaling

```bash
# Scale web application
kubectl scale deployment data-web-app --replicas=5

# Scale PostgreSQL (not recommended for production - use managed services)
kubectl scale deployment data-web-app-postgres --replicas=1
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Structure

- **Models**: Data models (Pydantic and SQLAlchemy)
- **Schemas**: Request/response validation schemas
- **Repositories**: Data access layer (CSV and PostgreSQL)
- **Services**: Business logic
- **API**: FastAPI route handlers

### Adding New Features

1. Add model in `app/models/`
2. Add schema in `app/schemas/`
3. Add repository interface/method in `app/repositories/`
4. Add service logic in `app/services/`
5. Add API route in `app/api/`

## Security Considerations

### Production Checklist

- [ ] Change all default passwords
- [ ] Set `APP_SECRET_KEY` to a strong random value
- [ ] Disable debug mode (`APP_DEBUG=False`)
- [ ] Configure proper CORS settings
- [ ] Use HTTPS with valid certificates
- [ ] Set appropriate resource limits in Kubernetes
- [ ] Configure proper network policies
- [ ] Use managed PostgreSQL service in production
- [ ] Enable database backups
- [ ] Configure monitoring and alerting

### Secrets Management

For production, use Kubernetes secrets or external secret managers:

```bash
# Create secrets from literal values
kubectl create secret generic postgres-secrets \
  --from-literal=db-name=data_app \
  --from-literal=db-user=myuser \
  --from-literal=db-password=mypassword

# Create secrets from environment variables
kubectl create secret generic postgres-secrets \
  --from-env-file=.env.secrets
```

## Troubleshooting

### Common Issues

1. **Database connection failed:**
   - Check `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
   - Ensure PostgreSQL is running and accessible
   - Check network connectivity between containers

2. **CSV file not found:**
   - Check `CSV_DIRECTORY` setting
   - Ensure the directory exists and has proper permissions
   - Verify file names and extensions

3. **Memory issues:**
   - Increase memory limits in Kubernetes manifests
   - Optimize queries for large datasets
   - Use pagination for large result sets

### Debugging

```bash
# Enable debug mode
APP_DEBUG=True

# View application logs
docker-compose logs web

# Kubernetes logs
kubectl logs -f deployment/data-web-app

# Exec into container
docker exec -it data-web-app sh
kubectl exec -it deployment/data-web-app -- sh
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

**Data Web Application** - Modern data manipulation web service for Docker and Kubernetes
