# FastAPI Medical Data Analytics Setup Guide

## Issues Fixed

1. **Database Connection**: Updated database URL to use correct database name (`medical_data` instead of `telegram_medical_data`)
2. **Column Name Mismatches**: Fixed queries to use `chat_title` instead of `channel_name` where appropriate
3. **Error Handling**: Added comprehensive error handling and logging
4. **Database Validation**: Added startup checks for database connectivity

## Quick Start

### 1. Ensure Database is Running

Make sure PostgreSQL is running with the correct database:

```bash
# Check if Docker containers are running
docker ps

# If not running, start the database
docker-compose up -d postgres
```

### 2. Install Dependencies

```bash
# Activate virtual environment
venv312\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Server

#### Option A: Using the startup script (Recommended)
```bash
python start_fastapi.py
```

#### Option B: Direct execution
```bash
python -m fastapi_app.main_new
```

### 4. Test the API

Once the server is running, you can:

- Visit http://localhost:8000/docs for interactive API documentation
- Test health endpoint: http://localhost:8000/health
- Test root endpoint: http://localhost:8000/

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. **Check if PostgreSQL is running**:
   ```bash
   docker ps | grep postgres
   ```

2. **Verify database exists**:
   ```bash
   docker exec -it <postgres_container_id> psql -U postgres -d medical_data
   ```

3. **Check database URL**:
   The app now uses: `postgresql://postgres:your_password_here@localhost:5432/medical_data`

### Port 8000 Already in Use

If port 8000 is already in use:

1. **Kill existing processes**:
   ```bash
   # Find process using port 8000
   netstat -ano | findstr :8000
   
   # Kill the process (replace PID with actual process ID)
   taskkill /PID <PID> /F
   ```

2. **Or use the startup script** which automatically handles this:
   ```bash
   python start_fastapi.py
   ```

### Import Errors

If you see import errors:

1. **Make sure you're in the correct directory**:
   ```bash
   cd "C:\Users\Admin\OneDrive\ACADEMIA\10 Academy\Week 7\GitHub Repository\telegram-medical-data-pipeline"
   ```

2. **Activate virtual environment**:
   ```bash
   venv312\Scripts\activate
   ```

3. **Run as module**:
   ```bash
   python -m fastapi_app.main_new
   ```

## API Endpoints

### Health Check
- `GET /health` - Check server and database status

### Analytics
- `GET /api/statistics` - Get comprehensive statistics
- `GET /api/reports/top-products` - Get most mentioned medical products
- `GET /api/channels/{channel_name}/activity` - Get channel activity over time
- `GET /api/search/messages` - Search messages with full-text search

### Data Access
- `GET /api/channels` - Get all channels
- `GET /api/messages` - Get messages with pagination
- `GET /api/medical-insights` - Get medical insights
- `GET /api/messages/{message_id}` - Get specific message

## Database Schema

The app uses the following tables:
- `fct_messages` - Main messages table
- `dim_channels` - Channel dimension table
- `fct_medical_insights` - Medical insights (if available)

## Logging

The app now includes comprehensive logging. Check the console output for:
- Database connection status
- API request logs
- Error details

## Testing

You can test the API using the Jupyter notebook `fastAPI.ipynb` which includes:
- Health checks
- Endpoint testing
- Data visualization
- Performance metrics

## Common Issues and Solutions

### Issue: "No module named 'fastapi_app'"
**Solution**: Run as module: `python -m fastapi_app.main_new`

### Issue: "Database connection failed"
**Solution**: 
1. Ensure PostgreSQL is running
2. Check database name is `medical_data`
3. Verify password is `your_password_here`

### Issue: "Column 'channel_name' does not exist"
**Solution**: The app now uses `chat_title` column instead of `channel_name`

### Issue: "Port 8000 already in use"
**Solution**: Use the startup script which automatically kills existing processes

## Next Steps

1. **Test all endpoints** using the interactive docs at http://localhost:8000/docs
2. **Run the Jupyter notebook** to test the API comprehensively
3. **Monitor logs** for any remaining issues
4. **Customize queries** in `crud.py` if needed for your specific data

## Support

If you encounter any issues:
1. Check the console logs for detailed error messages
2. Verify database connectivity using the health endpoint
3. Test individual endpoints using the Swagger UI
4. Review the troubleshooting section above 