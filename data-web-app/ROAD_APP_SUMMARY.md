# Road - Travel Management Application

## 📋 Application Summary

**Road** is a complete web application for managing travel trips with an AI assistant. The application follows the "Station F Vibe" design aesthetic with a modern, responsive interface.

## ✨ Features Implemented

### 1. **User Authentication**
- Hardcoded user: `Paloma` / `laBest`
- JWT token-based authentication
- Session persistence in localStorage
- Login/logout endpoints

### 2. **Trip Management**
- Create trips with: name, description, start/end dates, status (draft/validated), GPS location
- View all trips in a table with sorting and filtering
- View trip details with statistics
- Edit, delete, duplicate trips
- Visualize trips on a world map

### 3. **Step Management**
- Add steps to trips with:
  - Name
  - Category: transport, hébergement, activité, food, sport, hobbies
  - Type (specific to category, e.g., train, plane, hotel, restaurant)
  - Start/end datetime
  - Start/end locations with GPS coordinates
  - Notes
  - Color (auto-assigned based on category)
  - Order index (for sequencing)
- View steps in a table
- Edit, delete, duplicate steps
- Drag and drop to reorder steps
- Filter steps by category
- Visualize steps on a map:
  - Transport steps: shown as start and end points connected by an arrow
  - Other categories: shown as single point
  - Color-coded by category

### 4. **AI Assistant**
- Chat interface with AI travel assistant
- Get travel suggestions based on trip context
- AI provides structured proposals that can be added as steps
- Conversation history per trip
- Integration with Google Maps links

### 5. **Design**
- Modern "Station F Vibe" aesthetic
- Color scheme: Primary purple (#4F46E5), with category-specific colors
- Responsive design: works on mobile, tablet, and desktop
- Interactive maps using Leaflet
- Clean, professional interface

### 6. **Data Persistence**
- Automatic save (all changes are immediately persisted via API)
- PostgreSQL database backend
- SQLAlchemy ORM for data modeling

## 📁 Project Structure

```
road-app/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py             # Base SQLAlchemy models
│   │   ├── user.py             # User model
│   │   ├── trip.py             # Trip model
│   │   ├── step.py             # Step model
│   │   └── shared_trip.py      # Shared trip model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # User schemas
│   │   ├── trip.py             # Trip schemas
│   │   ├── step.py             # Step schemas
│   │   ├── shared_trip.py      # Shared trip schemas
│   │   └── ai.py               # AI schemas
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py             # Base repository interface
│   │   ├── base_repository.py  # Async base repository
│   │   ├── user_repository.py  # User repository
│   │   ├── trip_repository.py  # Trip repository
│   │   ├── step_repository.py  # Step repository
│   │   └── shared_trip_repository.py  # Shared trip repository
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication service
│   │   ├── trip_service.py     # Trip business logic
│   │   ├── step_service.py     # Step business logic
│   │   └── ai_service.py       # AI service (mock implementation)
│   │
│   └── api/
│       ├── __init__.py
│       ├── auth.py             # Authentication routes
│       ├── trips.py            # Trip routes
│       ├── steps.py            # Step routes
│       ├── ai.py               # AI routes
│       └── health.py           # Health check routes
│
├── static/
│   ├── index.html             # Main HTML file
│   ├── css/
│   │   └── style.css           # Complete CSS with Station F Vibe design
│   └── js/
│       ├── config.js           # Configuration and state
│       ├── utils.js            # Utility functions
│       ├── api.js              # API client
│       ├── ui.js               # UI manager
│       ├── auth.js             # Authentication manager
│       ├── view.js             # View manager
│       ├── trips.js            # Trip manager
│       ├── steps.js            # Step manager
│       ├── map.js              # Map manager (Leaflet)
│       ├── ai.js               # AI manager
│       ├── events.js           # Event listeners
│       └── app.js              # Main application entry point
│
├── scripts/
│   └── init_road.sql          # PostgreSQL database initialization
│
├── data/
│   └── csv/
│
├── k8s/
│   └── ...
│
├── nginx/
│   └── nginx.conf
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🚀 How to Run

### 1. Prerequisites
- Python 3.8+
- PostgreSQL (or use CSV for development)
- pip

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env` and update as needed:
```bash
cp .env.example .env
```

For PostgreSQL configuration:
```ini
APP_NAME=Road
APP_DATA_SOURCE=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=road_app
DB_USER=postgres
DB_PASSWORD=your_password
```

### 4. Initialize Database
Run the SQL script to create tables:
```bash
psql -U postgres -d road_app -f scripts/init_road.sql
```

Or use the existing PostgreSQL repository.

### 5. Run the Application
```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application will be available at:
- http://localhost:8000
- API Docs: http://localhost:8000/docs
- API Redoc: http://localhost:8000/redoc

### 6. Docker (Optional)
```bash
# Build and run with Docker Compose
docker-compose up -d

# The app will be available at http://localhost:8000
```

## 🎯 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Login with username/password |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/auth/logout` | Logout |
| POST | `/api/v1/auth/verify` | Verify token |

### Trips
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/trips/` | List all trips (with filters) |
| GET | `/api/v1/trips/table` | List trips for table display |
| GET | `/api/v1/trips/{id}` | Get trip details |
| POST | `/api/v1/trips/` | Create a new trip |
| PUT | `/api/v1/trips/{id}` | Update a trip |
| DELETE | `/api/v1/trips/{id}` | Delete a trip |
| POST | `/api/v1/trips/{id}/duplicate` | Duplicate a trip |
| GET | `/api/v1/trips/{id}/map` | Get trip map data |
| GET | `/api/v1/trips/categories/colors` | Get category colors |

### Steps
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/steps/` | List steps for a trip |
| GET | `/api/v1/steps/table` | List steps for table display |
| GET | `/api/v1/steps/{id}` | Get step details |
| POST | `/api/v1/steps/` | Create a new step |
| PUT | `/api/v1/steps/{id}` | Update a step |
| DELETE | `/api/v1/steps/{id}` | Delete a step |
| POST | `/api/v1/steps/{id}/duplicate` | Duplicate a step |
| POST | `/api/v1/steps/reorder` | Reorder steps |
| GET | `/api/v1/steps/categories` | Get all categories |
| GET | `/api/v1/steps/transport-types` | Get transport types |
| GET | `/api/v1/steps/colors` | Get category colors |

### AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/chat` | Chat with AI assistant |
| GET | `/api/v1/ai/conversation/{trip_id}` | Get conversation history |
| DELETE | `/api/v1/ai/conversation/{trip_id}` | Clear conversation |
| POST | `/api/v1/ai/proposal` | Add AI proposal as step |
| GET | `/api/v1/ai/proposals/suggestions` | Get AI suggestions |

## 🎨 Frontend Features

### Design Elements
- **Color Palette**: Primary purple (#4F46E5) with category-specific colors
- **Typography**: Inter font family
- **Components**: Cards, tables, modals, toasts, buttons, filters
- **Responsive**: Mobile-first design with breakpoints at 480px, 768px, 1024px

### Pages
1. **Login Screen** - Authentication form with demo credentials
2. **Home Page** - Trip table + world map visualization
3. **Trip Detail Page** - 
   - Trip information card
   - Step table with filtering
   - Interactive map with all steps
   - AI chat section

### Interactive Features
- Click trip names to view details
- Drag and drop to reorder steps
- Filter trips by status
- Filter steps by category
- Chat with AI for travel suggestions
- Add AI proposals as steps

## 🔐 Authentication

The application includes a hardcoded user for demo purposes:
- **Username**: Paloma
- **Password**: laBest

The authentication uses JWT tokens stored in localStorage.

## 📊 Data Models

### User
```python
class User:
    id: int
    username: str
    password_hash: str
    full_name: Optional[str]
    email: Optional[str]
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    trips: List[Trip]
    shared_trips: List[SharedTrip]
```

### Trip
```python
class Trip:
    id: int
    name: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime
    status: TripStatus  # 'brouillon' or 'validé'
    latitude: Optional[float]
    longitude: Optional[float]
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    owner: User
    steps: List[Step]
    shared_with: List[SharedTrip]
```

### Step
```python
class Step:
    id: int
    name: str
    category: StepCategory  # transport, hébergement, activité, food, sport, hobbies
    type: Optional[str]
    start_datetime: datetime
    end_datetime: Optional[datetime]
    location_start: Optional[str]
    location_end: Optional[str]
    latitude_start: Optional[float]
    longitude_start: Optional[float]
    latitude_end: Optional[float]
    longitude_end: Optional[float]
    notes: Optional[str]
    order_index: int
    color: Optional[str]
    trip_id: int
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    trip: Trip
```

### SharedTrip
```python
class SharedTrip:
    id: int
    user_id: int  # Owner
    shared_with_user_id: int
    trip_id: int
    can_edit: bool = False
    can_delete: bool = False
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    user: User
    shared_with_user: User
    trip: Trip
```

## 🎯 Architecture

The application follows a clean architecture pattern:

1. **Models** - SQLAlchemy ORM models for database tables
2. **Schemas** - Pydantic models for request/response validation
3. **Repositories** - Data access layer (abstraction over database)
4. **Services** - Business logic layer
5. **API** - FastAPI route handlers
6. **Frontend** - Static HTML/CSS/JS with responsive design

## 🛠️ Technologies Used

### Backend
- FastAPI - Web framework
- SQLAlchemy - ORM
- PostgreSQL - Database
- Pydantic - Data validation
- JWT - Authentication
- httpx - HTTP client for AI integration

### Frontend
- Vanilla JavaScript (ES6+) - No framework needed
- Leaflet - Interactive maps
- Font Awesome - Icons
- Google Fonts (Inter) - Typography
- CSS3 - Styling with CSS variables

### DevOps
- Docker - Containerization
- Docker Compose - Multi-container orchestration
- Kubernetes - Production deployment (config included)

## 🎨 Design: Station F Vibe

The application features a modern, startup-inspired design:

- **Primary Color**: Purple (#4F46E5) - Modern tech feel
- **Secondary Color**: Indigo (#6366F1)
- **Success**: Green (#10B981)
- **Warning**: Orange (#F59E0B)
- **Danger**: Red (#EF4444)
- **Info**: Blue (#3B82F6)

Category colors:
- Transport: Blue (#3B82F6)
- Hébergement: Green (#10B981)
- Activité: Orange (#F59E0B)
- Food: Red (#EF4444)
- Sport: Purple (#8B5CF6)
- Hobbies: Pink (#EC4899)

## 💡 AI Integration

The AI service provides:
- Natural language chat interface
- Context-aware suggestions based on trip data
- Structured proposals that can be added as steps
- Google Maps link integration
- Conversation history per trip

**Note**: The AI implementation currently uses mock responses. To enable real AI:
1. Add your Mistral API key to the configuration
2. Uncomment and configure the API calls in `ai_service.py`
3. Implement proper proposal parsing in the frontend

## 📈 Future Enhancements

1. **Real AI Integration** - Connect to Mistral AI API
2. **Google Maps API** - For address geocoding
3. **Multi-user Support** - Full user registration
4. **Trip Sharing** - Implement sharing functionality
5. **Export/Import** - Export trips to PDF/CSV
6. **Weather Integration** - Show weather for trip locations
7. **Budget Tracking** - Add budget management
8. **Notifications** - Email/SMS notifications

## 📝 Notes

- The application is designed to be **mobile-responsive**
- All changes are **auto-saved** via API calls
- Data is **user-isolated** (except when explicitly shared)
- The design follows **Station F Vibe** aesthetic
- The frontend is a **Single Page Application (SPA)**

## 🎓 Usage Tips

1. **Login**: Use `Paloma` / `laBest` for demo
2. **Create Trip**: Click "Nouveau Voyage" button
3. **Add Steps**: In trip detail, click "Ajouter une étape"
4. **Reorder Steps**: Drag and drop in the step table
5. **Filter**: Use category tabs to filter steps
6. **AI Chat**: Type questions in the chat input at the bottom

## 🐛 Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Run the init script: `psql -f scripts/init_road.sql`

### Frontend Loading Issues
- Check browser console for errors
- Verify all JS files are loaded in correct order
- Clear browser cache

### API Errors
- Check `/docs` for API documentation
- Verify authentication token is present
- Use `/api/v1/health` to check API status

## 📜 License

This application is built on the existing `data-web-app` framework and extends it for travel management purposes.

---

**Road - Travel Management Application**
*Built with FastAPI, PostgreSQL, and Vanilla JavaScript*
