📁 Project Structure
data-web-app/
├── app/                          # Application code
│   ├── main.py                  # FastAPI entry point
│   ├── config.py               # Configuration (CSV & PostgreSQL)
│   ├── models/                 # Data models (Pydantic + SQLAlchemy)
│   ├── schemas/                # Request/response schemas
│   ├── repositories/           # Data access layer
│   │   ├── csv_repository.py   # CSV implementation
│   │   └── postgres_repository.py # PostgreSQL implementation
│   ├── services/               # Business logic
│   └── api/                    # FastAPI routes
├── data/                        # Data files
│   ├── csv/                    # CSV datasets (with sample file)
│   └── uploads/                # Upload directory
├── k8s/                        # Kubernetes manifests
│   ├── deployment.yaml         # Deployments (web + postgres)
│   ├── service.yaml           # Services
│   ├── ingress.yaml           # Ingress
│   ├── pvc.yaml               # Persistent volumes
│   └── secrets.yaml           # Secrets
├── nginx/                      # Nginx reverse proxy config
├── scripts/                   # Database init script
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Local development stack
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # Complete documentation
✨ Features
Core Functionality
•
✅ CSV file data manipulation
•
✅ PostgreSQL database integration
•
✅ REST API with FastAPI
•
✅ Data querying with filters, sorting, pagination
•
✅ Dataset statistics and metadata
•
✅ File upload support
Docker & Kubernetes
•
✅ Dockerfile with multi-stage builds
•
✅ Docker Compose for local development (web + PostgreSQL + pgAdmin)
•
✅ Kubernetes manifests (deployments, services, ingress, PVC, secrets)
•
✅ Nginx reverse proxy configuration
•
✅ Health checks and readiness probes
•
✅ Resource limits and scaling configuration
Architecture
•
✅ Clean architecture (Models, Schemas, Repositories, Services, API)
•
✅ Dependency injection
•
✅ Async/await support
•
✅ Repository pattern (easy to switch between CSV and PostgreSQL)
•
✅ Proper error handling
•
✅ Configuration management with Pydantic
🚀 Quick Start
1. Install & Run (CSV mode - default)
cd data-web-app
pip install -r requirements.txt
uvicorn app.main:app --reload
2. Docker Compose (full stack)
docker-compose up -d
# Access at: http://localhost:8000
# API Docs: http://localhost:8000/docs
# pgAdmin: http://localhost:5050
3. Kubernetes
# Build and push image
docker build -t your-registry/data-web-app:latest .
docker push your-registry/data-web-app:latest

# Deploy to Kubernetes
kubectl apply -f k8s/
🔧 Configuration
Switch between CSV and PostgreSQL by setting DATA_SOURCE=csv or DATA_SOURCE=postgres in your .env file.
📄 API Endpoints
Method
Endpoint
Description
GET
/api/v1/datasets/
List all datasets
POST
/api/v1/datasets/
Create a new dataset
GET
/api/v1/datasets/{name}
Get dataset details
DELETE
/api/v1/datasets/{name}
Delete a dataset
POST
/api/v1/datasets/{name}/upload
Upload CSV file
POST
/api/v1/datasets/{name}/query
Query dataset data
GET
/api/v1/datasets/{name}/columns
Get column info
GET
/api/v1/datasets/{name}/stats
Get dataset statistics
The project is production-ready and follows best practices for Docker and Kubernetes deployment. You can start with CSV files and seamlessly transition to PostgreSQL when needed! 🎉