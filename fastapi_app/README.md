# Telegram Medical Data Analytics API

A FastAPI application for serving analytics endpoints from medical data extracted from Telegram channels.

## Features

- **SQLAlchemy ORM**: Modern database access with type safety
- **Analytics Endpoints**: Pre-built analytics queries for medical data
- **Full-text Search**: Search across messages, channels, and users
- **Channel Activity**: Daily/weekly/monthly activity tracking
- **Product Analytics**: Top mentioned products across channels
- **Swagger Documentation**: Auto-generated API documentation

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `fastapi_app` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/telegram_medical_data

# FastAPI Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_RELOAD=true
```

### 3. Database Setup

Ensure your PostgreSQL database is running and contains the required tables:
- `dim_channels`
- `dim_dates`
- `fct_messages`
- `fct_medical_insights`
- `raw_messages`
- `enriched_messages`
- `processed_images`

## Running the Application

### Development Mode

```bash
cd fastapi_app
python main_new.py
```

### Using Uvicorn Directly

```bash
cd fastapi_app
uvicorn main_new:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Core Analytics Endpoints

#### 1. Top Products Report
```
GET /api/reports/top-products?limit=10
```
Returns most frequently mentioned products from medical insights.

#### 2. Channel Activity
```
GET /api/channels/{channel_name}/activity?period=daily&limit=30
```
Returns daily/weekly/monthly post counts and activity metrics.

#### 3. Message Search
```
GET /api/search/messages?query=paracetamol&limit=50
```
Full-text search across messages with relevance scoring.

### Additional Endpoints

- `GET /api/statistics` - Comprehensive analytics statistics
- `GET /api/channels` - List all channels
- `GET /api/messages` - Get messages with filtering
- `GET /api/medical-insights` - Get medical insights
- `GET /api/messages/{message_id}` - Get specific message

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Schema

The application uses the following main tables:

### Fact Tables
- `fct_messages`: Main message data with channel and date relationships
- `fct_medical_insights`: Medical analysis results with sentiment and entities

### Dimension Tables
- `dim_channels`: Channel information
- `dim_dates`: Date dimension for time-based analytics

### Raw Tables
- `raw_messages`: Original scraped messages
- `enriched_messages`: Enriched message data
- `processed_images`: Image analysis results

## Query Examples

### Get Top Products
```python
import requests

response = requests.get("http://localhost:8000/api/reports/top-products?limit=5")
products = response.json()
```

### Search for Medical Terms
```python
response = requests.get("http://localhost:8000/api/search/messages?query=paracetamol")
results = response.json()
```

### Channel Activity Analysis
```python
response = requests.get("http://localhost:8000/api/channels/medical_channel/activity?period=weekly")
activity = response.json()
```

## Error Handling

The API includes comprehensive error handling:
- **400 Bad Request**: Invalid parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Database or application errors

## Performance Considerations

- Database indexes are used for optimal query performance
- Pagination is implemented for large result sets
- Connection pooling is configured for database efficiency
- Full-text search uses PostgreSQL capabilities

## Development

### Adding New Endpoints

1. Add the endpoint to `main_new.py`
2. Create corresponding CRUD function in `crud.py`
3. Add response schema to `schemas.py` if needed
4. Update documentation

### Database Migrations

Use Alembic for database migrations:

```bash
alembic init alembic
alembic revision --autogenerate -m "Add new table"
alembic upgrade head
```

## Testing

Test the API using the Swagger UI or with curl:

```bash
# Health check
curl http://localhost:8000/health

# Get top products
curl "http://localhost:8000/api/reports/top-products?limit=5"

# Search messages
curl "http://localhost:8000/api/search/messages?query=medicine"
``` 