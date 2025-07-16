# Dagster Pipeline Setup

This document describes the Dagster pipeline setup for the Telegram medical data pipeline.

## Overview

The Dagster pipeline orchestrates the following operations:

1. **scrape_telegram_data**: Scrapes data from Telegram channels using Telethon
2. **load_raw_to_postgres**: Parses JSON data and loads to PostgreSQL raw database
3. **run_dbt_transformations**: Runs dbt transformations via subprocess
4. **run_yolo_enrichment**: Processes images with YOLO for medical content detection
5. **generate_pipeline_report**: Generates comprehensive execution report

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Telegram API credentials
- YOLO model files

### Install Dependencies

```bash
# Install Dagster and other dependencies
pip install -r requirements.txt

# Verify Dagster installation
dagster --version
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Telegram API Configuration
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Data Paths
RAW_DATA_PATH=data/raw
PROCESSED_DATA_PATH=data/processed
```

### Dagster Configuration

The pipeline uses `dagster.yaml` for workspace configuration:

```yaml
workspace:
  - module_name: dags.telegram_pipeline

instance:
  sqlite:
    base_dir: ".dagster"

scheduler:
  enabled: true
```

## Usage

### 1. Test the Setup

Run the test script to verify everything is configured correctly:

```bash
python scripts/test_dagster.py
```

### 2. Start Dagster UI

Launch the Dagster development server:

```bash
dagster dev
```

This will start the Dagster UI at `http://localhost:3000`

### 3. Run Pipeline Manually

Execute the pipeline directly:

```bash
python dags/telegram_pipeline.py
```

### 4. Monitor Scheduled Runs

The pipeline is scheduled to run every 24 hours at 2 AM. Monitor scheduled runs in the Dagster UI.

## Pipeline Operations

### scrape_telegram_data

- **Purpose**: Scrapes messages from configured Telegram channels
- **Input**: None (uses hardcoded channel list)
- **Output**: Dict with scrape results and metadata
- **Error Handling**: Logs connection failures and scraping errors
- **Logging**: Detailed logs for each channel processed

### load_raw_to_postgres

- **Purpose**: Loads scraped JSON data to PostgreSQL
- **Input**: Scrape results from previous operation
- **Output**: Dict with load results and record counts
- **Error Handling**: Skips loading if scraping failed
- **Logging**: Reports files processed and records loaded

### run_dbt_transformations

- **Purpose**: Executes dbt models, tests, and documentation
- **Input**: None (works with data in database)
- **Output**: Dict with dbt execution results
- **Error Handling**: Fails fast on configuration errors
- **Logging**: Detailed logs for each dbt command

### run_yolo_enrichment

- **Purpose**: Processes images with YOLO for medical content
- **Input**: None (scans for images in raw data directory)
- **Output**: Dict with processing results and detection counts
- **Error Handling**: Gracefully handles missing images
- **Logging**: Reports images processed and detections found

### generate_pipeline_report

- **Purpose**: Creates comprehensive execution summary
- **Input**: Results from all previous operations
- **Output**: Dict with pipeline execution report
- **Error Handling**: Collects errors from all operations
- **Logging**: Final pipeline status and metrics

## Scheduling

The pipeline includes a daily schedule:

```python
@schedule(
    job=telegram_pipeline_job,
    cron_schedule="0 2 * * *",  # 2 AM daily
    default_status=DefaultScheduleStatus.RUNNING,
    description="Daily Telegram medical data pipeline"
)
def daily_telegram_pipeline_schedule(context):
    return {}
```

## Monitoring and Logging

### Logging Configuration

All operations use Dagster's built-in logging:

```python
logger = get_dagster_logger()
logger.info("Operation started")
logger.error("Error occurred")
```

### Error Handling

Each operation includes comprehensive error handling:

- Connection failures
- Data processing errors
- File system errors
- Database errors

### Metrics and Reporting

The pipeline generates detailed reports including:

- Messages scraped per channel
- Records loaded to database
- Images processed with YOLO
- dbt transformation success/failure
- Overall pipeline status

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path includes project root

2. **Telegram Connection Issues**
   - Verify API credentials in `.env`
   - Check internet connectivity
   - Ensure phone number is correct

3. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check database URL format
   - Ensure database exists

4. **dbt Issues**
   - Verify dbt project configuration
   - Check profiles.yml setup
   - Ensure dbt dependencies are installed

### Debug Commands

```bash
# Test Dagster setup
python scripts/test_dagster.py

# Check Dagster workspace
dagster workspace list

# View pipeline definition
dagster job list

# Execute specific operation
dagster job execute telegram_pipeline_job
```

## Development

### Adding New Operations

1. Create new `@op` function in `dags/telegram_pipeline.py`
2. Add proper error handling and logging
3. Update job definition to include new operation
4. Test with `dagster dev`

### Modifying Schedules

Edit the schedule decorator in `dags/telegram_pipeline.py`:

```python
@schedule(
    job=telegram_pipeline_job,
    cron_schedule="0 */6 * * *",  # Every 6 hours
    default_status=DefaultScheduleStatus.RUNNING
)
def custom_schedule(context):
    return {}
```

### Configuration Management

Add configuration to operations:

```python
@op(config_schema={"max_messages": int})
def custom_op(context):
    max_messages = context.op_config["max_messages"]
    # ... operation logic
```

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]
```

### Environment Variables

Set production environment variables:

```bash
export TELEGRAM_API_ID=your_production_api_id
export TELEGRAM_API_HASH=your_production_api_hash
export DATABASE_URL=your_production_database_url
```

### Monitoring

- Use Dagster's built-in monitoring
- Set up external monitoring (e.g., Prometheus)
- Configure alerting for pipeline failures
- Monitor resource usage

## Security Considerations

- Store sensitive credentials in environment variables
- Use secure database connections
- Implement proper access controls
- Regular security updates for dependencies

## Performance Optimization

- Parallel execution where possible
- Batch processing for large datasets
- Resource monitoring and scaling
- Caching for repeated operations 