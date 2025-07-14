{{
  config(
    materialized='view'
  )
}}

select
    id,
    raw_message_id,
    medical_entities,
    sentiment_score,
    urgency_level,
    processed_at
from {{ source('raw', 'enriched_messages') }} 