# Telegram dbt Project

This dbt project transforms raw Telegram message data into a structured data warehouse for analysis.

## 🏗️ Project Structure

```
dbt/
├── models/
│   ├── staging/
│   │   ├── stg_telegram_messages.sql
│   │   └── schema.yml
│   ├── marts/
│   │   ├── dim_channels.sql
│   │   ├── dim_dates.sql
│   │   ├── fct_messages.sql
│   │   └── schema.yml
│   └── sources.yml
├── tests/
│   └── test_messages_have_channel_name.sql
├── macros/
│   └── generate_docs.sql
├── dbt_project.yml
├── profiles.yml
└── README.md
```

## 📊 Data Models

### Staging Layer
- **`stg_telegram_messages`**: Normalized and cleaned raw messages
  - Normalizes column names and types
  - Extracts `has_image` boolean from media information
  - Preserves all original data in `raw_data` column

### Marts Layer
- **`dim_channels`**: Channel dimension table
  - One row per unique channel
  - Contains channel metadata and information
  
- **`dim_dates`**: Calendar dimension table
  - One row per date in the data range
  - Includes year, month, day, day of week, season, etc.
  
- **`fct_messages`**: Fact table for messages
  - Joins messages with dimension tables
  - Contains all message details and foreign keys

## 🔧 Setup

### 1. Environment Variables
Ensure your `.env` file contains:
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=telegram_medical
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

### 2. Install dbt
```bash
pip install dbt-core dbt-postgres
```

### 3. Test Connection
```bash
cd dbt
dbt debug
```

## 🚀 Usage

### Run Models
```bash
# Run all models
dbt run

# Run specific model
dbt run --select stg_telegram_messages

# Run marts only
dbt run --select marts
```

### Run Tests
```bash
# Run all tests
dbt test

# Run specific test
dbt test --select test_messages_have_channel_name
```

### Generate Documentation
```bash
# Generate docs
dbt docs generate

# Serve docs locally
dbt docs serve
```

## 🧪 Tests

### Built-in Tests
- **Unique**: `message_id`, `channel_id`, `date_id`
- **Not Null**: `message_id`, `channel_name`, `channel_id`

### Custom Tests
- **`test_messages_have_channel_name`**: Ensures all messages have a channel name

## 📈 Data Flow

```
Raw Data (raw.telegram_messages)
    ↓
Staging (stg_telegram_messages)
    ↓
Dimensions (dim_channels, dim_dates)
    ↓
Fact Table (fct_messages)
```

## 🔍 Sample Queries

### Message Count by Channel
```sql
SELECT 
    channel_name,
    COUNT(*) as message_count
FROM {{ ref('fct_messages') }}
GROUP BY channel_name
ORDER BY message_count DESC;
```

### Messages with Images
```sql
SELECT 
    channel_name,
    COUNT(*) as total_messages,
    SUM(CASE WHEN has_image THEN 1 ELSE 0 END) as messages_with_images,
    ROUND(SUM(CASE WHEN has_image THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as image_percentage
FROM {{ ref('fct_messages') }}
GROUP BY channel_name;
```

### Daily Message Volume
```sql
SELECT 
    d.date_id,
    d.day_name,
    COUNT(*) as message_count
FROM {{ ref('fct_messages') }} f
JOIN {{ ref('dim_dates') }} d ON f.date_id = d.date_id
GROUP BY d.date_id, d.day_name
ORDER BY d.date_id;
```

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check PostgreSQL is running
   - Verify environment variables in `.env`
   - Test connection with `dbt debug`

2. **Model Errors**
   - Check source table exists: `raw.telegram_messages`
   - Verify column names match source schema
   - Run `dbt run --select stg_telegram_messages` first

3. **Test Failures**
   - Check for null values in required columns
   - Verify data quality in source table
   - Review custom test logic

## 📚 Documentation

After running `dbt docs generate`, you can view:
- Model lineage and dependencies
- Column descriptions and tests
- Data freshness information
- Source table documentation

## 🔄 Refresh Data

To refresh the entire pipeline:
```bash
dbt clean
dbt deps
dbt run
dbt test
dbt docs generate
``` 