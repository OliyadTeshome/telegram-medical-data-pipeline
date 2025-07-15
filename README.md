# Telegram Medical Data Pipeline

A production-ready Python data pipeline for extracting, processing, and analyzing medical data from Telegram channels using modern data engineering tools.

## 🏗️ Architecture

This pipeline consists of the following components:

- **Telegram Scraper**: Uses Telethon to extract messages from medical channels
- **PostgreSQL**: Data warehouse for storing raw and processed data
- **YOLOv8**: Image enrichment using computer vision for medical content detection
- **dbt**: Data modeling and transformation layer
- **FastAPI**: REST API for serving insights and analytics
- **Dagster**: Orchestration and workflow management
- **Docker**: Containerization for easy deployment

## 📁 Project Structure

```
telegram-medical-data-pipeline/
├── src/
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── telegram_scraper.py          # Async Telegram scraper with media download
│   ├── loader/
│   │   ├── __init__.py
│   │   └── postgres_loader.py           # PostgreSQL data loader
│   ├── enrich/
│   │   ├── __init__.py
│   │   └── yolo_enricher.py            # YOLOv8 image analysis
│   ├── dbt_runner/
│   │   ├── __init__.py
│   │   └── dbt_executor.py             # dbt execution utilities
│   └── utils/
│       ├── __init__.py
│       └── config.py                   # Configuration management
├── dbt/
│   ├── dbt_project.yml                 # dbt project configuration
│   ├── profiles.yml                    # Database connection profiles
│   ├── models/                         # Data transformation models
│   ├── macros/                         # Reusable SQL macros
│   ├── tests/                          # Data quality tests
│   ├── create_models.sql              # Database schema creation
│   ├── run_models.py                  # dbt execution script
│   └── README.md                      # dbt documentation
├── fastapi_app/
│   ├── __init__.py
│   └── main.py                        # FastAPI application with endpoints
├── dags/
│   ├── __init__.py
│   └── telegram_pipeline.py           # Dagster orchestration pipeline
├── scripts/
│   ├── run_scraper.py                 # Standalone scraper execution
│   ├── test_scraper.py                # Scraper testing script
│   ├── load_telegram_messages.py      # Data loading utilities
│   ├── test_db_connection.py          # Database connection testing
│   └── README_telegram_loader.md      # Loader documentation
├── notebooks/
│   ├── scraping.ipynb                 # Jupyter notebook for scraping
│   ├── transform.ipynb                # Data transformation notebook
│   ├── model.ipynb                    # Model development notebook
│   └── data/                          # Notebook data files
├── docs/
│   ├── TELEGRAM_SCRAPER_SETUP.md      # Detailed scraper setup guide
│   └── CI_CD_SETUP.md                 # CI/CD pipeline documentation
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py                # Scraper unit tests
│   └── test_loader.py                 # Loader unit tests
├── Dockerfile                         # Docker container definition
├── docker-compose.yml                 # Multi-service orchestration
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Project metadata and tooling config
├── init.sql                          # Database initialization script
└── README.md                         # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Telegram API credentials (API ID, API Hash, Phone Number)

### Environment Setup

1. **Clone the repository**
```bash
git clone (https://github.com/OliyadTeshome/telegram-medical-data-pipeline.git)
cd telegram-medical-data-pipeline
```

2. **Set up environment variables**
```bash
# Copy environment template
cp env.example .env

# Edit .env with your credentials
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=your_phone_number_here
POSTGRES_PASSWORD=your_secure_password_here
```

### Telegram API Setup

1. Visit https://my.telegram.org/
2. Log in with your phone number
3. Create a new application
4. Copy the API ID and API Hash to your `.env` file

### Running the Pipeline

#### Option 1: Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

#### Option 2: Individual Components

**Test the scraper:**
```bash
python scripts/test_scraper.py
```

**Run the scraper:**
```bash
python scripts/run_scraper.py
```

**Test database connection:**
```bash
python scripts/test_db_connection.py
```

**Run dbt transformations:**
```bash
cd dbt
python run_models.py
```

### Access Services

- **FastAPI**: http://localhost:8000
- **Dagster UI**: http://localhost:3000
- **PostgreSQL**: localhost:5432

## 🔧 Configuration

### Target Channels

The scraper is configured to scrape these medical channels:
- `https://t.me/CheMed123`
- `https://t.me/lobelia4cosmetics`
- `https://t.me/tikvahpharma`

### Pipeline Configuration

Edit the pipeline configuration in `dags/telegram_pipeline.py`:

```python
def get_pipeline_config():
    return {
        "ops": {
            "scrape_telegram_messages": {
                "config": {
                    "channels": ["@CheMed123", "@lobelia4cosmetics", "@tikvahpharma"],
                    "limit": 1000
                }
            }
        }
    }
```

## 📊 Data Flow

1. **Extraction**: Telegram messages are scraped from configured channels using async Telethon
2. **Storage**: Raw data is stored in PostgreSQL with date-based organization
3. **Enrichment**: 
   - Text messages are analyzed for medical entities and sentiment
   - Images are processed with YOLOv8 for medical content detection
4. **Transformation**: dbt models transform raw data into analytics-ready tables
5. **Serving**: FastAPI provides REST endpoints for data access and insights

## 🛠️ API Endpoints

### Health Check
```bash
GET /health
```

### Messages
```bash
GET /messages?limit=100&offset=0&channel=medical_channel
GET /messages/enriched?limit=100&offset=0
GET /messages/search?query=covid&limit=50
```

### Analytics
```bash
GET /statistics
GET /channels
GET /images/analysis?limit=100&offset=0
```

## 🔄 Pipeline Orchestration

The Dagster pipeline orchestrates the entire data flow:

1. **Scrape Messages**: Extract from Telegram channels using async Telethon
2. **Load to PostgreSQL**: Store raw data with proper error handling
3. **Process Images**: YOLO analysis for medical content detection
4. **Enrich Messages**: Medical entity extraction and sentiment analysis
5. **Run dbt**: Transform data into analytics models
6. **Generate Report**: Pipeline execution summary

## 📈 Data Models

### Raw Tables
- `raw_messages`: Scraped Telegram messages with metadata
- `processed_images`: YOLO analysis results with confidence scores
- `enriched_messages`: Medical analysis and sentiment data

### Analytics Models
- `fct_medical_insights`: Fact table with medical insights
- `stg_raw_messages`: Staging view for raw messages
- `stg_enriched_messages`: Staging view for enriched data

## 🔍 Monitoring

### Dagster UI
- Access at http://localhost:3000
- Monitor pipeline runs and logs
- Configure schedules and sensors

### FastAPI Health Check
```bash
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

### Common Issues

1. **Telegram Authentication**
   - Ensure API credentials are correct
   - Check phone number format (include country code)
   - Verify session file permissions

2. **Database Connection**
   - Check PostgreSQL service is running
   - Verify connection parameters in `.env`
   - Ensure database exists and is accessible

3. **YOLO Model**
   - Model downloads automatically on first run
   - Check internet connection for model download
   - Verify sufficient disk space

### Logs

```bash
# View all service logs
docker-compose logs

# View specific service
docker-compose logs app
docker-compose logs postgres
```

## 🔒 Security Considerations

- Store sensitive credentials in environment variables
- Use strong passwords for PostgreSQL
- Consider using secrets management for production
- Implement proper authentication for FastAPI endpoints
- Regular security updates for dependencies

## 📝 Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run individual components
python -m src.scraper.telegram_scraper
python -m fastapi_app.main
```

### Testing

```bash
# Test scraper functionality
python scripts/test_scraper.py

# Test database connection
python scripts/test_db_connection.py

# Test dbt configuration
cd dbt && dbt debug

# Run unit tests
pytest tests/ -v
```

### Code Quality

The project includes comprehensive code quality tools:

```bash
# Format code
black src/ fastapi_app/ dags/ scripts/

# Sort imports
isort src/ fastapi_app/ dags/ scripts/

# Lint code
flake8 src/ fastapi_app/ dags/ scripts/

# Type checking
mypy src/ fastapi_app/ dags/ scripts/
```

## 🚀 CI/CD Pipeline

This project includes a comprehensive CI/CD pipeline using GitHub Actions:

### Workflows

- **CI Pipeline**: Code quality, testing, and Docker building
- **Security Scanning**: Dependency and container security checks
- **Deployment**: Automated Docker image deployment

### Features

- ✅ **Code Quality**: Black formatting, isort, flake8 linting, mypy type checking
- ✅ **Testing**: pytest with coverage reporting and PostgreSQL integration
- ✅ **Security**: Safety dependency scanning, Trivy container scanning, TruffleHog secrets detection
- ✅ **Deployment**: Automated Docker image building and pushing to GitHub Container Registry
- ✅ **Dependency Management**: Dependabot for automated dependency updates

For detailed CI/CD documentation, see [docs/CI_CD_SETUP.md](docs/CI_CD_SETUP.md).

## 📚 Documentation

- [Telegram Scraper Setup](docs/TELEGRAM_SCRAPER_SETUP.md) - Detailed setup guide for the Telegram scraper
- [CI/CD Setup](docs/CI_CD_SETUP.md) - Complete CI/CD pipeline documentation
- [dbt Documentation](dbt/README.md) - Data transformation and modeling guide

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run local CI checks before submitting
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Telethon](https://docs.telethon.dev/) for Telegram API access
- [Ultralytics](https://github.com/ultralytics/ultralytics) for YOLOv8
- [dbt](https://docs.getdbt.com/) for data transformation
- [Dagster](https://docs.dagster.io/) for orchestration
- [FastAPI](https://fastapi.tiangolo.com/) for API development 

